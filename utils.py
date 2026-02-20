# utils.py
import os
import datetime
import json
from IPython.display import Image, display

def save_graph_image(app, thread_id="default"):
    """Saves a Mermaid PNG of the graph structure"""
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Graphs")
    os.makedirs(output_dir, exist_ok=True)

    try:
        png_data = app.get_graph().draw_mermaid_png()
        output_path = os.path.join(output_dir, f"graph_{thread_id}.png")
        
        with open(output_path, "wb") as f:
            f.write(png_data)
        
        print(f"Graph saved to: {output_path}")
        # Note: display() only works in Jupyter environments
        try:
            display(Image(png_data))
        except:
            pass
    except Exception as e:
        print(f"Could not generate graph image (requires mermaid/graphviz support): {e}")

def save_execution_log(log_data, thread_id):
    """Saves the execution history to a formatted text file"""
    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Logs")
    os.makedirs(log_dir, exist_ok=True)
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"log_{thread_id}_{timestamp}.txt"
    filepath = os.path.join(log_dir, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"EXECUTION LOG - Thread ID: {thread_id}\n")
        f.write(f"Timestamp: {timestamp}\n")
        f.write("="*80 + "\n\n")

        for step_num, entry in enumerate(log_data, 1):
            f.write(f"--- STEP {step_num}: {entry['node']} ---\n")
            f.write(json.dumps(entry['output'], indent=4, default=str))
            f.write("\n\n")
        
        f.write("="*80 + "\n")
        
    return filepath