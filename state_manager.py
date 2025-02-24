import json
import os

STATE_FILE = "test_state.json"

def load_state():
    """טוען את המצב האחרון מקובץ JSON"""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as file:
            try:
                state = json.load(file)
                if "counter1" in state and "counter2" in state and "name_index" in state and "last_user_index" in state:
                    return state
            except json.JSONDecodeError:
                print("Error: Corrupted or empty JSON file. Resetting state.")
    return {"counter1": 1, "counter2": 1, "name_index": 0, "last_user_index": 0}

def save_state(state):
    """שומר את המצב הנוכחי לקובץ JSON"""
    with open(STATE_FILE, "w") as file:
        json.dump(state, file)

def get_next_name():
    """יוצר שם חדש על בסיס המצב השמור"""
    state = load_state()

    name_list = ["brain_write", "bad_idea", "Combine", "perspective", "hobbies", "Bio Mimic", "Less is More", "trends"]

    name = f"test_{name_list[state['name_index']]}_{state['counter1']}_{state['counter2']}"

    # עדכון המצב
    state["counter2"] += 1
    if state["counter2"] > 3:  # מעגל של 1-3
        state["counter2"] = 1
        state["name_index"] += 1
        if state["name_index"] >= len(name_list):
            state["name_index"] = 0
            state["counter1"] += 1

    save_state(state)
    return name

def get_next_user(user_list):
    """מקבל את המשתמש הבא מהרשימה ושומר את המצב"""
    if not user_list:
        raise ValueError("User list is empty.")

    state = load_state()
    last_user_index = state["last_user_index"]

    # חישוב המשתמש הבא (מעגלי)
    next_user_index = (last_user_index + 1) % len(user_list)

    # עדכון המצב
    state["last_user_index"] = next_user_index
    save_state(state)

    # החזרת המשתמש הבא (המתוקן!)
    return user_list[next_user_index]
