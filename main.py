# main.py
from langchain.messages import HumanMessage
from langgraph.types import Command
import uuid

# Import custom modules
from graph import create_email_graph
from utils import save_graph_image

def main():
    # 1. Initialize Graph
    app = create_email_graph()
    
    # Generate a thread ID for memory persistence
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    
    # Save a visual representation of the graph
    save_graph_image(app, thread_id)
    
    print(f"Session initialized with Thread ID: {thread_id}")

    # 2. Define Initial Input
    email_text = "I am extremely frustrated! I checked my credit card statement and was billed twice for my Pro Plan this month. On top of that, when I try to log into the dashboard to cancel my subscription, I just get a blank white screen. Please refund my extra charge immediately and fix this login bug. My team is completely blocked. Can't fill tje gifting form either"
    # email_text = input("Enter the email content (or press Enter to use default): ") 
    initial_state = {
        "email_content": [HumanMessage(content=email_text)],
        "sender_email": "angry.manager@techcorp.com",
        "email_id": "email_999_complex"
    }

    print("\n🚀 Starting Email Agent Workflow...\n")
    
    # 3. Run the graph until interrupt or completion
    app.invoke(initial_state, config)
    
    # 4. Check State (Human-in-the-loop Logic)
    state_snapshot = app.get_state(config)
    
    # If state_snapshot.next has a value, the graph is paused (waiting for input)
    if state_snapshot.next:
        # Extract the data passed into the interrupt() call
        pending_task = state_snapshot.tasks[0]
        interrupt_payload = pending_task.interrupts[0].value
        
        # Display the review UI
        print("="*60)
        print(" 🛑 HUMAN REVIEW REQUIRED 🛑")
        print("="*60)
        print(f"Original Email:\n{interrupt_payload['original_email']}\n")
        print(f"Classification: Intent -> {interrupt_payload['intent'].upper()} | Urgency -> {interrupt_payload['urgency'].upper()}")
        print("-" * 60)
        print(f"Drafted Response:\n{interrupt_payload['draft_response']}\n")
        print("="*60)
        
        # User Interaction Loop
        while True:
            user_input = input("Action (approve [y] / reject [n] / edit [e]): ").strip().lower()
            
            if user_input in ['y', 'yes']:
                resume_data = {"approved": True}
                break
            elif user_input in ['e', 'edit']:
                print("\nEnter your edited response below (Press Enter when done):")
                new_response = input("> ")
                resume_data = {"approved": True, "edited_response": new_response}
                break
            elif user_input in ['n', 'no']:
                print("\nResponse rejected. Ending workflow without sending.")
                resume_data = {"approved": False}
                break
            else:
                print("Invalid input. Please type 'y', 'n', or 'e'.")
                
        # Resume the graph
        print("\nResuming workflow...")
        app.invoke(Command(resume=resume_data), config)
        
    else:
        print("\nWorkflow completed automatically (No review required).")
        
    print("\n✅ Execution Finished.")

if __name__ == "__main__":
    main()