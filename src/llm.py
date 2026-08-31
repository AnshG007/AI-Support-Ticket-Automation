import os
import sys

from dotenv import load_dotenv

from langchain_groq import ChatGroq

def create_llm():
    load_dotenv()

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key or api_key.strip() in {"" , "your_api_key_here"}:
        print("Error: GROQ_API_KEY is missing")
        sys.exit(1)
    model_name = os.getenv("GROQ_MODEL")
    return ChatGroq(model = model_name , temperature = 0)