import json
from typing import List, Dict
from datetime import datetime, timedelta


def load_json(json_path: str) -> List[Dict]:
    """
    Loads a JSON file and returns its contents as a list of dictionaries.

    Args:
        json_path (str): Path to the JSON file.

    Returns:
        List[Dict]: Parsed JSON content.
    """
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data

def get_user_progress(json_path: str) -> dict:
    """
    return user progress

    Args:
        json_path (str): path to JSON file.
    Returns:
        dict: days and status
    """
    data = load_json(json_path)
    day_data = data[0]
    return {day: info["status"] for day, info in day_data.items()}

def update_day_status(json_path: str, day: str, new_status: str) -> None:
    """
    Updates the status of a given day in the progress_db.json file.
    
    Args:
        path (str): Path to progress_db.json
        day (str): The day to update (e.g., "day_1")
        new_status (str): The new status ("completed", "unlocked", "locked")
    
    Returns:
        dict: The updated progress dictionary
    """
    try:
        # Load JSON
        data = load_json(json_path)

        # Since data is a list with one dict inside
        progress = data[0]

        if day not in progress:
            print(f"{day} not found in progress database.")

        # Update only the status
        progress[day]["status"] = new_status

        # Write back to file
        with open(json_path, "w") as f:
            json.dump([progress], f, indent=2)
        return None
    except Exception as e:
        print(f"Failed to update {day}: {str(e)}")

def get_motivation_message(json_path: str, day: str) -> str:
    """
    Fetch motivational message for the given day from progress DB
    """
    progress_data = load_json(json_path)
    if not progress_data or day not in progress_data[0]:
        print(f"Day {day} not found in progress database")
    return progress_data[0][day]["message"]

def load_questions(json_path: str, day: str) ->List[dict]:
    """
    load and return all the questions
    """
    day_to_skip = ["day_7", "day_8"]
    data = load_json(json_path)
    if day in day_to_skip:
        return data
    selected_keys = ["id", "type", "question", "options", "order", "topic"]
    return [
        {key: item[key] for key in selected_keys if key in item}
        for item in data
    ]


def write_passed_date(passed_date_file: str, day: str) -> None:
    """
    Write the day and current timestamp into passed_date.txt
    Format: <day>|<iso_timestamp>
    """
    try:
        with open(passed_date_file, "w") as f:
            f.write(f"{day}|{datetime.utcnow().isoformat()}")
    except Exception as e:
        raise Exception(f"{str(e)}")

def get_last_completed_date(passed_date_file: str) -> datetime | None:
    """
    Return the last completed day (or None if not available).
    """
    try:
        with open(passed_date_file, "r") as f:
            content = f.read().strip()
        day, last_date = content.split("|")
        return datetime.fromisoformat(last_date)
    except Exception as e:
        raise Exception(f"{str(e)}")