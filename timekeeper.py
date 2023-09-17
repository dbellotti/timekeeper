import sys
import os
import json
import datetime
import argparse
from collections import defaultdict

FILENAME = "time_tracking.json"


def load_data():
    if os.path.exists(FILENAME):
        with open(FILENAME, "r") as f:
            return json.load(f)
    return {}


def save_data(data):
    with open(FILENAME, "w") as f:
        json.dump(data, f, indent=4)


def start_time(category, data):
    current_time = str(datetime.datetime.now())
    if category not in data:
        data[category] = []
    data[category].append({"start": current_time})
    print(f"Started time for {category} at {current_time}")


def end_time(category, data):
    current_time = str(datetime.datetime.now())
    if category not in data:
        print(f"No start time found for {category}")
        return

    last_entry = data[category][-1]
    if "end" in last_entry:
        print(f"Last entry for {category} already has an end time. Please start time first.")
        return

    last_entry["end"] = current_time
    print(f"Ended time for {category} at {current_time}")


def summarize(data, period):
    period_summary = defaultdict(lambda: defaultdict(datetime.timedelta))

    for category, times in data.items():
        for entry in times:
            if "start" in entry and "end" in entry:
                start = datetime.datetime.fromisoformat(entry["start"])
                end = datetime.datetime.fromisoformat(entry["end"])
                delta = end - start

                if period == "daily":
                    key = start.date()
                elif period == "weekly":
                    key = start.date().isocalendar()[1]
                elif period == "monthly":
                    key = start.date().replace(day=1)
                else:
                    print("Invalid period")
                    return

                period_summary[key][category] += delta

    for key, categories in sorted(period_summary.items()):
        print(f"Period: {key}")
        for category, total_time in categories.items():
            print(f"  {category}: {total_time}")


def main():
    parser = argparse.ArgumentParser(description="Time tracking utility")
    parser.add_argument("command", help="Command to execute (e.g., sum, project name)")
    parser.add_argument("--period", choices=["daily", "weekly", "monthly"], help="Time period for summary")

    args = parser.parse_args()
    command = args.command
    period = args.period

    data = load_data()

    if command == "sum":
        if period:
            summarize(data, period)
        else:
            print("Please provide a period flag (--daily, --weekly, --monthly) for the summary.")
    else:
        category = command
        if not category:
            print("Please provide a category.")
            return

        last_entry = data.get(category, [])[-1] if data.get(category) else None

        if last_entry is None or "end" in last_entry:
            start_time(category, data)
        else:
            end_time(category, data)

        save_data(data)


if __name__ == "__main__":
    main()

