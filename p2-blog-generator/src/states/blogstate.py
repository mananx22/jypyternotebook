# =============================================================================
# blogstate.py
# Defines the data models (state schema) used throughout the LangGraph
# blog generation workflow.
# =============================================================================

# TypedDict: Used to define BlogState as a typed dictionary schema for
# LangGraph, specifying the keys and their value types.
from typing import TypedDict

# BaseModel: Pydantic base class for defining validated data models.
# Field: Used to attach metadata (e.g., descriptions) to model fields.
from pydantic import BaseModel, Field


# --- DATA MODELS -----------------------------------------------------------

class Blog(BaseModel):
    # """
    # Pydantic model representing a generated blog post.
    #
    # Attributes:
    #     title (str): The title of the blog post.
    #     content (str): The full body/content of the blog post.
    # """

    # title: The generated blog title, with a description for LLM guidance.
    title: str = Field(description="title for the blog")

    # content: The generated blog body text, with a description for LLM guidance.
    content: str = Field(description="description for the blog")


class BlogState(TypedDict):
    # """
    # TypedDict defining the state schema for the LangGraph blog workflow.
    #
    # This dictionary flows through every node in the graph. Each node reads
    # from it and returns partial updates that LangGraph merges automatically.
    #
    # Attributes:
    #     topic (str): The input topic provided by the user.
    #     blog (Blog): A Blog object holding the generated title and content.
    #     current_state (str): A string tracking the current processing state.
    # """

    topic: str
    blog: Blog
    current_language: str
