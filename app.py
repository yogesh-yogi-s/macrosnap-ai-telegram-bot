import asyncio
import concurrent.futures

import streamlit as st
from google import genai
from google.genai import types
from telegram import Bot

from prompts import SUMMARY_REQUEST_PROMPT, SYSTEM_PROMPT, WELCOME_MESSAGE_TEMPLATE

# App page configuration
st.set_page_config(page_title="MacroSnap - Telegram AI Vision", page_icon="🥗", layout="centered")

# Retrieve and validate required secrets
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "")
TELEGRAM_BOT_TOKEN = st.secrets.get("TELEGRAM_BOT_TOKEN", "")
MODEL_NAME = st.secrets.get("GEMINI_MODEL", "gemini-3.8-flash")

if not GEMINI_API_KEY or not TELEGRAM_BOT_TOKEN:
    st.error(
        "⚠️ **Missing Configuration Secrets**\n\n"
        "Please create `.streamlit/secrets.toml` based on `.streamlit/secrets.toml.example` "
        "and configure `GEMINI_API_KEY` and `TELEGRAM_BOT_TOKEN`."
    )
    st.stop()


@st.cache_resource
def get_gemini_client():
    return genai.Client(api_key=GEMINI_API_KEY)


gemini_client = get_gemini_client()


def render_message(message):
    with st.chat_message(message["role"]):
        if message["kind"] == "text":
            st.write(message["content"])
        elif message["kind"] == "image":
            st.image(message["content"])


def add_message(role, kind, content):
    st.session_state.messages.append({"role": role, "kind": kind, "content": content})
    render_message(st.session_state.messages[-1])


def ask_gemini(parts):
    try:
        return st.session_state.chat.send_message(parts).text
    except Exception as error:
        return f"Sorry, something went wrong: {error}"


def clean_telegram_text(text):
    if not text:
        return "No nutrition summary available."
    text = text.strip()
    return text[:4000] + "\n...(truncated)" if len(text) > 4000 else text


def send_telegram(chat_id, text):
    try:
        bot = Bot(token=TELEGRAM_BOT_TOKEN)

        async def _send():
            return await bot.send_message(chat_id=chat_id, text=clean_telegram_text(text))

        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            with concurrent.futures.ThreadPoolExecutor() as executor:
                message = executor.submit(asyncio.run, _send()).result()
        else:
            message = asyncio.run(_send())

        return True, f"Telegram message sent (ID: {message.message_id})"
    except Exception as error:
        return False, str(error)


# Step 1: Onboarding
if "onboarded" not in st.session_state:
    st.title("🥗 MacroSnap")
    st.caption("Snap it. Track it. Send the results straight to Telegram.")

    with st.form("onboarding_form"):
        name = st.text_input("Your name")
        telegram_chat_id = st.text_input(
            "Telegram Chat ID",
            placeholder="e.g. 123456789",
            help="Your unique Telegram Chat ID. Get it instantly by messaging @userinfobot on Telegram.",
        )
        submitted = st.form_submit_button("Let's go 🚀")

    with st.expander("ℹ️ How to find your Telegram Chat ID"):
        st.markdown(
            """
            1. Open Telegram and search for **[@userinfobot](https://t.me/userinfobot)**.
            2. Press **Start** (or send any text). It will reply with your numeric **Id** (e.g., `123456789`).
            3. **Important**: Also open your own Telegram bot and tap **Start** (or send a greeting) so it has permission to message you.
            """
        )

    if submitted:
        if not name.strip() or not telegram_chat_id.strip():
            st.warning("Please fill in both your name and Telegram Chat ID.")
        else:
            st.session_state.name = name.strip()
            st.session_state.telegram_chat_id = telegram_chat_id.strip()
            st.session_state.chat = gemini_client.chats.create(
                model=MODEL_NAME,
                config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT),
            )
            st.session_state.messages = []
            st.session_state.onboarded = True
            st.rerun()
    st.stop()


# Step 2: Chat Interface
header_col, button_col = st.columns([5, 2], vertical_alignment="center")

with header_col:
    st.title("🥗 MacroSnap")

with button_col:
    messages = st.session_state.get("messages", [])
    send_disabled = len(messages) <= 2
    if st.button("📤 Send to Telegram", disabled=send_disabled, use_container_width=True):
        with st.spinner("Summarizing your meals..."):
            summary = ask_gemini([SUMMARY_REQUEST_PROMPT])
        success, info = send_telegram(st.session_state.get("telegram_chat_id", ""), summary)
        if success:
            st.success("Sent! Check your Telegram 📲")
        else:
            st.error(f"Couldn't send to Telegram: {info}")

user_name = st.session_state.get("name", "User")
chat_id = st.session_state.get("telegram_chat_id", "")
st.caption(f"Logged in as **{user_name}** — updates go to Telegram Chat ID: `{chat_id}`")

if "messages" not in st.session_state:
    st.session_state.messages = []

if not st.session_state.messages:
    add_message("assistant", "text", WELCOME_MESSAGE_TEMPLATE.format(name=user_name))
else:
    for message in st.session_state.messages:
        render_message(message)

user_input = st.chat_input(
    "Ask a question, or attach a photo of your meal",
    accept_file=True,
    file_type=["jpg", "jpeg", "png"],
)

if user_input:
    photo = user_input.files[0] if user_input.files else None
    text = user_input.text
    parts = []

    if photo is not None:
        photo_bytes = photo.getvalue()
        add_message("user", "image", photo_bytes)
        parts.append(types.Part.from_bytes(data=photo_bytes, mime_type=photo.type))
    if text:
        add_message("user", "text", text)
        parts.append(text)
    elif photo is not None:
        parts.append("What is this meal? Give me the calories and macros.")

    with st.spinner("Crunching the numbers..."):
        answer = ask_gemini(parts)
    add_message("assistant", "text", answer)
