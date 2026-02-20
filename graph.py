# graph.py
from langgraph.graph import END, START, StateGraph
from langgraph.checkpoint.memory import InMemorySaver

# Import nodes and state
from states import EmailAgentState
import nodes

def create_email_graph():
    """Builds and compiles the email processing graph"""
    
    # Initialize Checkpointer
    memory = InMemorySaver()
    
    # Build Graph
    builder = StateGraph(EmailAgentState)

    # Add Nodes
    builder.add_node("read_email", nodes.read_email)
    builder.add_node("classify_intent", nodes.classify_intent)
    builder.add_node("search_documentation", nodes.search_documentation)
    builder.add_node("bug_tracking", nodes.bug_tracking)
    builder.add_node("write_response", nodes.write_response)
    builder.add_node("human_review", nodes.human_review)
    builder.add_node("send_reply", nodes.send_reply)

    # Add Edges
    builder.add_edge(START, "read_email")
    builder.add_edge("read_email", "classify_intent")
    builder.add_edge("classify_intent", "search_documentation")
    builder.add_edge("classify_intent", "bug_tracking")
    builder.add_edge("search_documentation", "write_response")
    builder.add_edge("bug_tracking", "write_response")
    builder.add_edge("send_reply", END)

    # Compile
    app = builder.compile(checkpointer=memory)
    return app