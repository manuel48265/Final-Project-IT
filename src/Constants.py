import os
from dotenv import load_dotenv
load_dotenv(dotenv_path="./keys.env")

CURRENCY_TYPES = ["USD", "PLN", "EUR", "GBP", "INR", "AUD", "CAD", "SGD", "CHF", "MYR", "JPY", "CNY", "LKR"]
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
MODEL_ID = "models/gemini-2.0-flash-exp"
TOKEN = os.getenv("TOKEN")