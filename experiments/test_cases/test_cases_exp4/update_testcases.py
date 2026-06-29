import json

MOVE_DELTA = {
    "up": (0, 1),
    "down": (0, -1),
    "left": (-1, 0),
    "right": (1, 0)
}

def process_file(input_file, output_file):
    with open(input_file, "r") as f:
        data = json.load(f)

    # ✅ If root is a list → process each entry
    if isinstance(data, list):
        for item in data:
            process_entry(item)
    else:
        # ✅ If it's a single object
        process_entry(data)

    with open(output_file, "w") as f:
        json.dump(data, f, indent=2)

    print("✅ Done!")


def process_entry(entry):
    current_x = entry["start"]["x"]
    current_y = entry["start"]["y"]

    moves = entry.get("moves", [])
    statuses = entry.get("responses", [])

    new_responses = []

    # initial state
    if len(statuses) > 0:
        new_responses.append([statuses[0], [current_x, current_y]])

    # apply moves
    for i, move in enumerate(moves):
        dx, dy = MOVE_DELTA.get(move, (0, 0))

        status = statuses[i + 1] if i + 1 < len(statuses) else "OK"

        if status == "BLOCKED":
            new_responses.append([status, [current_x, current_y]])
        else:
            current_x += dx
            current_y += dy
            new_responses.append([status, [current_x, current_y]])

    entry["responses"] = new_responses


# Run
process_file("test_20_300.json", "test_20_300_new.json")