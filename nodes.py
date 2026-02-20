# nodes.py
import json
import os
import uuid
from typing import Literal
from langgraph.types import Command, interrupt
from langgraph.graph import END

# Import shared state and config
from states import EmailAgentState, EmailClassification
from config import llm

def read_email(state: EmailAgentState) -> EmailAgentState:
    """Extract and parse email content"""
    # Logic placeholder
    pass

def classify_intent(state: EmailAgentState) -> EmailAgentState:
    """Use LLM to classify email intent and urgency"""
    
    # Create structured LLM that returns EmailClassification dict
    structured_llm = llm.with_structured_output(EmailClassification)

    classification_prompt = f"""
    Analyze this customer email and classify it:

    Email: {state['email_content']}
    From: {state['sender_email']}

    Provide classification, including intent, urgency, topic, and summary
    """

    # Get structured response directly as a dict
    classification = structured_llm.invoke(classification_prompt)

    return {"classification": classification}

def search_documentation(state: EmailAgentState) -> EmailAgentState:
    """
    Load knowledge base from JSON file and retrieve relevant docs.
    Replaces hardcoded dummy data with actual file I/O.
    """
    search_results = []
    
    # 1. Construct path to knowledge_base.json (assumed to be in same dir)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    kb_file_path = os.path.join(base_dir, "knowledge_base.json")
    
    try:
        # 2. Synchronously read the JSON file
        if os.path.exists(kb_file_path):
            with open(kb_file_path, "r", encoding="utf-8") as f:
                kb_data = json.load(f)
            
            # 3. Format data for the context window
            # Since the KB is small, we provide all docs to ensure the LLM 
            # has full context (Policies, Bugs, and Tone).
            if kb_data:
                for doc in kb_data:
                    doc_id = doc.get("id", "N/A")
                    category = doc.get("category", "General")
                    content = doc.get("content", "")
                    search_results.append(f"Doc ID {doc_id} ({category}): {content}")
            else:
                search_results = ["Knowledge base is empty."]
        else:
            search_results = [f"Error: Knowledge base file not found at {kb_file_path}"]
            
    except Exception as e:
        search_results = [f"Error loading documentation: {str(e)}"]

    return {"search_results": search_results}

def bug_tracking(state: EmailAgentState) -> EmailAgentState:
    """Create or update bug tracking ticket"""
    ticket_id = f"BUG_{uuid.uuid4()}"
    return {"ticket_id": ticket_id}

def write_response(state: EmailAgentState) -> Command[Literal["human_review", "send_reply"]]:
    """Generate response using context and route based on quality"""
    classification = state.get('classification', {})
    context_sections = []

    if state.get('search_results'):
        formatted_docs = "\n".join([f"- {doc}" for doc in state['search_results']])
        context_sections.append(f"Relevant documentation:\n{formatted_docs}")

    if state.get('customer_history'):
        context_sections.append(f"Customer tier: {state['customer_history'].get('tier', 'standard')}")

    draft_prompt = f"""
    Draft a response to this customer email:
    {state['email_content']}

    Email intent: {classification.get('intent', 'unknown')}
    Urgency level: {classification.get('urgency', 'medium')}

    {chr(10).join(context_sections)}

    Guidelines:
    - Be professional and helpful
    - Address their specific concern
    - Use the provided documentation when relevant
    - Be brief
    """

    response = llm.invoke(draft_prompt)

    # Determine if human review is needed
    needs_review = (
        classification.get('urgency') in ['high', 'critical'] or
        classification.get('intent') == 'complex'
    )

    if needs_review:
        goto = "human_review"
        print("Needs approval")
    else:
        goto = "send_reply"

    return Command(
        update = {"draft_response": response.content},
        goto = goto
    )

def human_review(state: EmailAgentState) -> Command[Literal["send_reply", END]]:
    """Pause for human review using interrupt and route based on decision"""
    classification = state.get('classification', {})

    # Interrupt execution and wait for input
    human_decision = interrupt({
        "email_id": state['email_id'],
        "original_email": state['email_content'],
        "draft_response": state.get('draft_response', ""),
        "urgency": classification.get('urgency'),
        "intent": classification.get('intent'),
        "action": "Please review and approve/edit this response"
    })

    if human_decision.get("approved"):
        return Command(
            update = {"draft_response": human_decision.get("edited_response", state['draft_response'])},
            goto = "send_reply"
        )
    else:
        return Command(update = {}, goto = END)

def send_reply(state: EmailAgentState) -> EmailAgentState:
    """Send the email response"""
    print(f"Sending reply: {state['draft_response'][:300]}...")
    return {}