# 🥗 MacroSnap — Telegram AI Vision App

MacroSnap is a Streamlit AI vision chatbot that allows you to snap or describe your meals, get instant calorie and macronutrient breakdowns from Google Gemini (chat + vision), and send a complete, concise nutrition summary directly to your Telegram chat with one click.

This project adapts the core MacroSnap architecture by replacing paid WhatsApp/Twilio messaging with a completely free Telegram Bot action tool.

---

## 🏗️ Architecture

```
User
  │
  ▼
Onboarding (Name + Telegram Chat ID)
  │
  ▼
Streamlit Chat Interface (Session State Memory)
  │
  ▼
Text Question or Meal Photo Input (JPG / PNG)
  │
  ▼
Google Gemini Vision & Chat (gemini-2.5-flash)
  │
  ▼
Conversation History & Follow-up Q&A
  │
  ▼
Hidden Summary Prompt (Gemini calculates meal totals & macros)
  │
  ▼
"📤 Send to Telegram" Action Button
  │
  ▼
Telegram Bot API (`send_telegram`)
  │
  ▼
Delivered to User's Telegram Chat 📲
```

---

## 💻 Required Software & Prerequisites

* **Python 3.9+** (Python 3.10, 3.11, 3.12, or 3.13 recommended)
* A free **Google AI Studio** account for a Gemini API Key
* A free **Telegram** account to create a bot and receive messages

---

## 🔑 Step-by-Step Setup Guide

### 1. Get a Free Gemini API Key
1. Go to [Google AI Studio](https://aistudio.google.com/).
2. Sign in with your Google account.
3. Click **Get API key** and generate a new key.
4. Keep this key handy for the secrets configuration.

### 2. Create a Free Telegram Bot
1. Open the Telegram app and search for **[@BotFather](https://t.me/BotFather)**.
2. Send `/start` and then send `/newbot`.
3. Choose a display name for your bot (e.g., `My MacroSnap Bot`).
4. Choose a unique username ending in `bot` (e.g., `my_macrosnap_vision_bot`).
5. BotFather will provide an **HTTP API Token** (e.g., `123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ`). Copy this token.

### 3. Send the First Message to Your Bot
Telegram requires users to initiate contact before a bot can message them:
1. Search for your new bot's username in Telegram.
2. Tap **Start** (or send `/start` or any greeting).

### 4. Find Your Telegram Chat ID
1. In Telegram, search for **[@userinfobot](https://t.me/userinfobot)** (or **[@RawDataBot](https://t.me/RawDataBot)**).
2. Tap **Start** (or send any text).
3. The bot will immediately reply with your numeric **Id** (e.g., `987654321`). This is your personal `chat_id`.

### 5. Configure Streamlit Secrets
1. In your project directory, copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml`:
   * On Windows (PowerShell):
     ```powershell
     Copy-Item .streamlit\secrets.toml.example .streamlit\secrets.toml
     ```
   * On macOS/Linux:
     ```bash
     cp .streamlit/secrets.toml.example .streamlit/secrets.toml
     ```
2. Open `.streamlit/secrets.toml` in your editor and insert your actual credentials:
   ```toml
   GEMINI_API_KEY = "AIzaSy..."
   TELEGRAM_BOT_TOKEN = "123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ"
   ```

> ⚠️ **Security Warning**: Never commit `.streamlit/secrets.toml` or expose your API keys in public repositories. Keep `.streamlit/secrets.toml` in `.gitignore` at all times.

---

## 🚀 Installation & Running Locally

### 1. Create and Activate a Virtual Environment
* **Windows (PowerShell)**:
  ```powershell
  python -m venv venv
  .\venv\Scripts\Activate.ps1
  ```
  *(If script execution is disabled, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` first)*

* **macOS / Linux**:
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Streamlit Application
```bash
streamlit run app.py
```
Streamlit will automatically launch the app in your browser at `http://localhost:8501`.

---

## 🔄 End-to-End Workflow

1. **Onboarding**: Enter your name and Telegram Chat ID. The app establishes a cached Gemini client and creates a persistent chat session with the nutrition system instructions.
2. **Text / Vision Chat**: 
   * Type meals or questions directly into the chat input.
   * Attach meal photos (`.jpg`, `.jpeg`, `.png`). The app converts images into `types.Part.from_bytes` and Gemini analyzes visual attributes (dish type, portion size, ingredients).
3. **Conversation Memory**: Gemini retains multi-turn context, allowing you to ask follow-up questions (e.g., *"How much protein was in that salad?"*).
4. **Summary & Telegram Action**:
   * Once you log meals, the **"📤 Send to Telegram"** button activates.
   * Clicking it sends a background prompt asking Gemini to condense all meals and calculate total calories and macros.
   * The app calls `send_telegram(chat_id, summary)` via `python-telegram-bot`, delivering the formatted recap straight to your phone.

---

## 📂 Project Structure

```
telegram-ai-vision/
│
├── app.py                     # Streamlit frontend, chat memory, Gemini vision & Telegram dispatcher
├── prompts.py                 # System persona, welcome message, and Telegram summary prompts
├── requirements.txt           # Minimal dependencies (streamlit, google-genai, python-telegram-bot)
├── README.md                  # Comprehensive setup and usage instructions
├── .gitignore                 # Excludes secrets.toml, venv/, and cache files
│
└── .streamlit/
    └── secrets.toml.example   # Secrets template for GEMINI_API_KEY and TELEGRAM_BOT_TOKEN
```
