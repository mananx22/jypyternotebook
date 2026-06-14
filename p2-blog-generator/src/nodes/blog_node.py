# Import the BlogState TypedDict which defines the structure of data
# that flows between nodes in the LangGraph workflow.
from src.states.blogstate import BlogState
from langchain_core.messages import SystemMessage,HumanMessage
from src.states.blogstate import Blog

# Define the BlogNode class that handles individual steps in the blog generation pipeline.
class BlogNode():

    # Constructor: accepts an LLM instance (e.g., ChatGroq) and stores it for later use.
    def __init__(self, llm):
        # Save the LLM reference so both node methods can invoke it.
        self.llm = llm

    # Node step 1: generates a creative blog title based on the topic in the state.
    def title_creation(self, state: BlogState):
        # Check that the state dictionary contains a valid (non-empty) "topic" key.
        if "topic" in state and state["topic"]:
            # Define a prompt template asking the LLM to act as a news reporter and create a title.
            # The {topic} placeholder will be replaced with the actual topic value.
            prompt = (
                "you are an expert news reporter. use markdown formatting. "
                "generate title for our blog, having topic as {topic}. make it creative. make it no more than 10 words."
            )
            # Replace {topic} in the prompt with the actual topic from the state.
            system_message = prompt.format(topic=state["topic"])
            # Invoke the LLM with the formatted prompt and get back a response object.
            response = self.llm.invoke(system_message)
            # Return a partial state update containing only the generated blog title.
            # LangGraph automatically merges this dictionary into the shared state.
            return {"blog": {"title": response.content}}

    # Node step 2: generates the full blog content using the topic, while preserving the title.
    def content_gen(self, state: BlogState):
        # Define a prompt template asking the LLM to write a detailed 70-line blog post.
        # The {topic} placeholder will be replaced with the actual topic value.
        system_prompt = (
            "you are an expert blog writer. use markdown formatting. "
            "generate detailed and 70 lines blog for the content having topic as {topic}"
        )
        # Replace {topic} in the prompt with the actual topic from the state.
        system_message = system_prompt.format(topic=state["topic"])
        # Invoke the LLM with the content-generation prompt and capture the response.
        response = self.llm.invoke(system_message)
        # Return a partial state update that carries forward the existing title
        # (created by title_creation) and adds the newly generated blog content.
        return {
            "blog": {
                "title": state["blog"]["title"],
                "content": response.content,
            }
        } 

    def translation(self, state: BlogState):
        # if "language" in state and state["language"]:
            print(state["current_language"])
            prompt = (
                "you are an expert linguistic of {current_language} language. "
                "You need to convert {topic} to {current_language} and {blog_content} as well. also they should be into the same format, tone."
            )
            blog_content = state["blog"]["content"]
            message=[
                 HumanMessage(prompt.format(current_language=state["current_language"], blog_content=blog_content, topic = state["topic"]))
            ]
            translation_content = self.llm.with_structured_output(Blog).invoke(message)
            return {"blog": {"content": translation_content}}
    
    def route(self, state:BlogState):
         return {"current_language": state['current_language']}
    
    def route_decision(self, state:BlogState):
         if state["current_language"] == "hindi":
              return "hindi"
         elif state['current_language'] == "french":
              return "french"
         else:
              return state['current_language']