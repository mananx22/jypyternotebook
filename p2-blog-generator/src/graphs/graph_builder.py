# =============================================================================
# graph_builder_commented.py
# Detailed line-by-line explanation of Graphbuilder
# =============================================================================

# --- IMPORTS ----------------------------------------------------------------

# StateGraph: The main class from LangGraph used to define a computational graph.
#              You add "nodes" (processing steps) and "edges" (transitions) to it.
# START:      A special sentinel constant representing the entry point of the graph.
# END:        A special sentinel constant representing the exit/terminal point.
from langgraph.graph import StateGraph, START, END

# Groqllm: A custom wrapper class (in src/llms/) that initializes and provides
#           a connection to the Groq LLM API (e.g., LLaMA, Mixtral models).
from src.llms.groqllm import Groqllm

# BlogState: A custom state class (in src/states/) that defines the schema/shape
#            of data that flows through the graph (e.g., fields like "topic",
#            "title", "content"). It acts as a shared memory between nodes.
from src.states.blogstate import BlogState

# BlogNode: A custom class (in src/nodes/) that contains the actual processing
#           logic for each step in the blog generation pipeline. Each method
#           in BlogNode takes the current state, does some work (like calling
#           the LLM), and returns an updated state.
from src.nodes.blog_node import BlogNode


# --- CLASS DEFINITION -------------------------------------------------------

class Graphbuilder:
    # """
    # Graphbuilder is responsible for constructing a LangGraph StateGraph
    # that defines the workflow for generating a blog post.
    #
    # The workflow (for the "topic" use case) is:
    #     START → title_creation → content_generation → END
    #
    # Usage:
    #     llm = Groqllm().get_llm()
    #     builder = Graphbuilder(llm)
    #     graph = builder.setup_graph(usecase="topic")
    #     result = graph.invoke({"topic": "some topic"})
    # """

    def __init__(self, llm):
        # """
        # Constructor: Initializes the Graphbuilder with a language model.
        #
        # Args:
        #     llm: A Groq LLM instance (or compatible) that will be used by
        #          the graph's nodes to generate text.
        #
        # What happens:
        #     1. Stores the LLM instance so it can be passed to nodes later.
        #     2. Creates a new StateGraph and tells it to use BlogState as its
        #        state schema. This means every node in the graph will receive
        #        and return a BlogState-like dictionary.
        # """
        # Save the LLM instance as an attribute so other methods can access it.
        self.llm = llm

        # Create a new StateGraph with BlogState as the state definition.
        # BlogState defines what keys/fields the state dict will have
        # (e.g., "topic", "title", "content"). The graph uses this to
        # validate and manage data flow between nodes.
        self.graph = StateGraph(BlogState)

    def build_topic_graph(self):
        # """
        # Builds the actual graph structure for the "topic" blog generation flow.
        #
        # This method:
        #     1. Creates a BlogNode instance (which holds the processing logic).
        #     2. Registers two processing nodes in the graph.
        #     3. Defines the edges (execution order) between nodes.
        #     4. Returns the configured (but not yet compiled) StateGraph.
        #
        # Returns:
        #     StateGraph: The configured graph with nodes and edges added.
        #                 Note: The caller must call .compile() on this before
        #                 it can be invoked.
        # """

        # Create a BlogNode object, passing in the LLM.
        # BlogNode contains methods like title_creation() and content_gen()
        # that define what each step in the pipeline does.
        self.blog_node_obj = BlogNode(self.llm)

        # --- REGISTER NODES ---
        # Add a node named "title creation" to the graph.
        # When this node executes, it will call self.blog_node_obj.title_creation(state),
        # which should use the LLM to generate a blog title from the topic.
        self.graph.add_node("title creation", self.blog_node_obj.title_creation)

        # Add a node named "content_generation" to the graph.
        # When this node executes, it will call self.blog_node_obj.content_gen(state),
        # which should use the LLM to generate the full blog content using
        # both the topic and the title produced by the previous node.
        self.graph.add_node("content_generation", self.blog_node_obj.content_gen)

        # --- DEFINE EDGES (execution flow) ---
        # Add an edge from START → "title creation"
        # This means the first thing that happens when the graph runs is
        # the title creation step.
        self.graph.add_edge(START, "title creation")

        # Add an edge from "title creation" → "content_generation"
        # After the title is generated, control flows to content generation.
        self.graph.add_edge("title creation", "content_generation")

        # Add an edge from "content_generation" → END
        # After the content is generated, the graph finishes.
        self.graph.add_edge("content_generation", END)

        # Return the configured graph.
        # IMPORTANT: The graph still needs to be compiled before use.
        # Compilation validates the graph structure and prepares it for execution.
        return self.graph

    def build_language_graph(self):
        self.blog_node_obj = BlogNode(self.llm)

        self.graph.add_node("title_creation", self.blog_node_obj.title_creation)
        self.graph.add_node("content_generation", self.blog_node_obj.content_gen)
        self.graph.add_node("hindi_translation", lambda state: self.blog_node_obj.translation({ **state, "current_language": "hindi"}))
        self.graph.add_node("french_translation", lambda state: self.blog_node_obj.translation({ **state, "current_lanugage": "french"}))
        self.graph.add_node("route", self.blog_node_obj.route)



        self.graph.add_edge(START, "title_creation")
        self.graph.add_edge("title_creation", "content_generation")
        self.graph.add_edge("content_generation", "route")

        # conditional edge
        self.graph.add_conditional_edges(
            "route",
            self.blog_node_obj.route_decision,
                {
                    "hindi" : "hindi_translation",
                    "french" : "french_translation"

                }      
        )
        self.graph.add_edge("hindi_translation", END)
        self.graph.add_edge("french_translation", END)
        return self.graph



    
    def setup_graph(self, usecase):
        # """
        # A factory/dispatcher method that selects and builds the appropriate
        # graph based on the requested use case.
        #
        # Args:
        #     usecase (str): A string identifying which graph to build.
        #                    Currently only "topic" is supported.
        #
        # Returns:
        #     StateGraph | None: The configured graph for the given use case,
        #                        or None if the use case is not recognized.
        #
        # BUG: Currently, when usecase == "topic", this method calls
        #    self.build_topic_graph() but does NOT return the result.
        #    This means it always returns None, and the caller will get
        #    an AttributeError when trying to call .invoke() on it.
        #
        #    Fix: Change `self.build_topic_graph()` to `return self.build_topic_graph()`
        # """

        # Check if the requested use case is "topic"
        if usecase == "topic":
            # Build and return the topic blog generation graph.
            self.build_topic_graph()
        if usecase == "language":
            self.build_language_graph()
        return self.graph.compile()

# below code is for langsmith, langgraph studio.
llm = Groqllm().get_llm()
graph_builder = Graphbuilder(llm)
graph=graph_builder.build_topic_graph().compile()
