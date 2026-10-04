import unittest
from streamlit.testing.v1 import AppTest
import prompts


class TestMacroSnapTelegram(unittest.TestCase):
    def test_prompts(self):
        """Verify that prompts contain expected personas, templates, and instructions."""
        self.assertIn("MacroSnap", prompts.SYSTEM_PROMPT)
        self.assertIn("nutrition", prompts.SYSTEM_PROMPT.lower())
        self.assertIn("{name}", prompts.WELCOME_MESSAGE_TEMPLATE)
        self.assertIn("Telegram", prompts.SUMMARY_REQUEST_PROMPT)

    def test_app_missing_secrets(self):
        """Verify that missing secrets show user-friendly error and stop execution."""
        at = AppTest.from_file("app.py")
        at.secrets["GEMINI_API_KEY"] = ""
        at.secrets["TELEGRAM_BOT_TOKEN"] = ""
        at.run()
        self.assertTrue(len(at.error) > 0)
        self.assertIn("Missing Configuration Secrets", at.error[0].value)

    def test_app_with_secrets_onboarding_view(self):
        """Verify that app displays the onboarding form when secrets are configured."""
        at = AppTest.from_file("app.py")
        at.secrets["GEMINI_API_KEY"] = "dummy-gemini-key"
        at.secrets["TELEGRAM_BOT_TOKEN"] = "123456:dummy-telegram-token"
        at.run()
        self.assertEqual(len(at.error), 0)
        self.assertTrue(any("MacroSnap" in title.value for title in at.title))
        input_labels = [inp.label for inp in at.text_input]
        self.assertIn("Your name", input_labels)
        self.assertIn("Telegram Chat ID", input_labels)

    def test_app_onboarding_empty_submission(self):
        """Verify that submitting empty fields in onboarding triggers a warning."""
        at = AppTest.from_file("app.py")
        at.secrets["GEMINI_API_KEY"] = "dummy-gemini-key"
        at.secrets["TELEGRAM_BOT_TOKEN"] = "123456:dummy-telegram-token"
        at.run()
        # Submit form with empty fields
        at.button[0].click().run()
        self.assertTrue(len(at.warning) > 0)
        self.assertIn("Please fill in both your name and Telegram Chat ID.", at.warning[0].value)

    def test_clean_telegram_text(self):
        """Verify text cleaning and truncation logic for Telegram."""
        import app
        self.assertEqual(app.clean_telegram_text(""), "No nutrition summary available.")
        self.assertEqual(app.clean_telegram_text("   Hello Telegram!   "), "Hello Telegram!")
        long_text = "A" * 5000
        truncated = app.clean_telegram_text(long_text)
        self.assertTrue(len(truncated) <= 4100)
        self.assertTrue(truncated.endswith("...(truncated)"))

    def test_telegram_send_invalid_token(self):
        """Verify that send_telegram catches and returns exceptions gracefully."""
        import app
        app.TELEGRAM_BOT_TOKEN = "invalid:token"
        success, info = app.send_telegram("123456789", "Test summary")
        self.assertFalse(success)
        self.assertTrue(len(info) > 0)


if __name__ == "__main__":
    unittest.main()
