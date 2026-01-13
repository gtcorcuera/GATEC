import json
import os

def load_data():
    """
    Loads data from data/data.json relative to the project root.
    Returns a dictionary containing card_data and predefined_values.
    """
    # Assuming this is called from within the package structure, we need to find the root
    # Adjust path as necessary.
    # Current file: gatec/core/data_manager.py
    # Data file: data/data.json
    
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    data_path = os.path.join(base_dir, 'data', 'data.json')
    
    try:
        with open(data_path, 'r') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        print(f"Error: Data file not found at {data_path}")
        return {"card_data": [], "predefined_values": {}}
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in {data_path}")
        return {"card_data": [], "predefined_values": {}}
