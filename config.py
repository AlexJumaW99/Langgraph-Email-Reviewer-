# config.py
import os
from dotenv import load_dotenv
from google import genai
from langchain_google_genai import ChatGoogleGenerativeAI

# Load environment variables
load_dotenv()

def list_gemini_models():
    """Helper to list available models"""
    try:
        client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])
        print(f"{'Model ID':<40} | {'Display Name'}")
        print("-" * 65)
        for model in client.models.list():
            if "gemini" in model.name:
                print(f"{model.name:<40} | {model.display_name}")
    except Exception as e:
        print(f"Error listing models: {e}")

def connect_to_llm():
    """Establishes connection to the Gemini LLM via LangChain"""
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash", 
        temperature=0, 
        max_tokens=10009, 
        timeout=120, 
        max_retries=3, 
    )
    return llm

# Create a singleton instance to be imported by nodes
llm = connect_to_llm()