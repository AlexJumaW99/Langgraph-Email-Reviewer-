import json
import os
from typing import List, Optional
from fastmcp import FastMCP

# 1. Initialize the FastMCP Server
mcp = FastMCP("Email Knowledge Base")

# 2. Define the Knowledge Base File
# This file will persist the JSON data you enter.
KB_FILE = "knowledge_base.json"

def load_knowledge_base() -> List[dict]:
    """Helper to load data from the JSON file."""
    if not os.path.exists(KB_FILE):
        return []
    try:
        with open(KB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []

def save_knowledge_base(data: List[dict]):
    """Helper to save data to the JSON file."""
    with open(KB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

# 3. Define Tools

@mcp.tool()
def search_documentation(query: str) -> List[str]:
    """
    Search the knowledge base for relevant documents based on a query.
    Returns a list of document strings.
    """
    data = load_knowledge_base()
    results = []
    
    # Simple case-insensitive keyword search
    query_lower = query.lower()
    for doc in data:
        content = doc.get("content", "")
        doc_id = doc.get("id", "Unknown ID")
        
        # Check if query matches content or ID
        if query_lower in content.lower() or query_lower in doc_id.lower():
            # Format matches the style expected by your graph
            results.append(f"Doc ID {doc_id}: {content}")
            
    if not results:
        return ["No relevant documentation found."]
        
    return results

@mcp.tool()
def add_document(id: str, content: str, category: str = "General") -> str:
    """
    Add a new document entry to the knowledge base (dummy data injection).
    """
    data = load_knowledge_base()
    
    # Check for duplicates
    for doc in data:
        if doc["id"] == id:
            return f"Error: Document with ID '{id}' already exists."

    new_doc = {
        "id": id,
        "content": content,
        "category": category
    }
    
    data.append(new_doc)
    save_knowledge_base(data)
    
    return f"Successfully added Doc ID {id} to the knowledge base."

@mcp.tool()
def list_all_documents() -> str:
    """Returns a formatted string of all documents in the system."""
    data = load_knowledge_base()
    if not data:
        return "The knowledge base is empty."
    
    summary = [f"- [{doc['id']}] {doc['content'][:50]}..." for doc in data]
    return "\n".join(summary)

# 4. Initialize with Default Dummy Data (Optional)
# This runs once on startup to ensure you have the data from your original nodes.py
if not os.path.exists(KB_FILE):
    initial_data = [
        {
            "id": "8492",
            "category": "Billing Policy",
            "content": "If a user reports being double-charged, verify their subscription status. If duplicate charges exist within a 24-hour window, automatically approve the refund for the most recent charge. Inform the customer that refunds take 7-8 business days to process."
        },
        {
            "id": "1022",
            "category": "Known Bugs",
            "content": "We are currently tracking a 'blank white screen on login' issue (Internal Ticket #UI-992). Workaround: Ask the user to clear their browser cache or use an Incognito/Private window. A permanent fix is scheduled for Patch 2.4 tomorrow."
        },
        {
            "id": "2271",
            "category": "Known Bugs",
            "content": "We are currently tracking a submission error when users try and fill our gifting form."
        },
        {
            "id": "551",
            "category": "General Tone",
            "content": "Always apologize for billing errors and express empathy when users are blocked by technical bugs."
        }
    ]
    save_knowledge_base(initial_data)

if __name__ == "__main__":
    # Run the server using the default STDIO transport
    mcp.run()