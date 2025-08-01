# utils.py
import json
import os

MEMORY_FILE = "memory.json"

def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return []
    with open(MEMORY_FILE, "r") as f:
        data = json.load(f)

    # Keep only the last few messages (max 4 exchanges = 8 messages)
    if len(data) > 4:
        data = data[-4:]

    return data


def save_memory(memory):
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=2)
