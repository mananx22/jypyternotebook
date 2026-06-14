# =============================================================================
# groqllm.py
# Wrapper around the Groq LLM API (via langchain-groq) that initializes
# and provides a ChatGroq instance for text generation.
# =============================================================================

# ChatGroq: LangChain integration for Groq Cloud's LLM API.
from langchain_groq import ChatGroq

# os: Used to set environment variables required by the Groq SDK.
import os

# load_dotenv: Loads environment variables from a .env file into os.environ.
from dotenv import load_dotenv

# SecretStr: Pydantic type that wraps sensitive strings (API keys) to
# prevent accidental logging or exposure.
from pydantic import SecretStr


class Groqllm:
    # """
    # Wrapper class that manages the creation of a Groq LLM instance.
    #
    # Responsibilities:
    #     - Loads environment variables from .env on initialization.
    #     - Provides a get_llm() method that returns a configured ChatGroq
    #       instance ready for text generation.
    #
    # Usage:
    #     llm = Groqllm().get_llm()
    # """

    def __init__(self):
        # """
        # Constructor: Loads environment variables from the .env file
        # so that GROQ_API_KEY is available via os.getenv() later.
        # """
        # Load .env file into environment variables.
        load_dotenv()

    def get_llm(self):
        # """
        # Creates and returns a configured ChatGroq LLM instance.
        #
        # Reads the GROQ_API_KEY from environment variables, sets it in
        # os.environ for the Groq SDK, and initializes ChatGroq with the
        # LLaMA 3.1 8B instant model.
        #
        # Returns:
        #     ChatGroq: A configured LLM instance ready for .invoke() calls.
        #
        # Raises:
        #     ValueError: If the LLM initialization fails for any reason.
        # """
        try:
            # Read the API key from env and store it both as an instance
            # attribute and in os.environ (required by the Groq SDK).
            os.environ["GROQ_API_KEY"] = self.groq_api_key = os.getenv(
                "GROQ_API_KEY", ""
            )

            # Initialize ChatGroq with the API key (wrapped in SecretStr
            # for secure handling) and the chosen model.
            llm = ChatGroq(
                api_key=SecretStr(self.groq_api_key),
                model="llama-3.1-8b-instant",
            )

            return llm
        except Exception as e:
            # Raise a clear error if initialization fails (e.g., bad API key).
            raise ValueError("Error occured : {e}")
        