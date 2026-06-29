import random
import json

# ---------------------------------------------------------------------------
# Board generation
# ---------------------------------------------------------------------------

def generate_board():
    all_squares = [(x, y) for x in range(1, 11) for y in range(1, 11)]
    random.shuffle(all_squares)
    traps = set(all_squares[:20])
    gold  = set(all_squares[20:30])
    return traps, gold

# ---------------------------------------------------------------------------
# Display helpers
# ---------------------------------------------------------------------------

def print_board_info(traps, gold):
    print("""I want to play the game below, read the rules, when you are ready prompt me for the path and I will give you my moves and you will respond as per the game instructions. This time I want you to only output the information specifically listed in the game so OK, OUCH, YIPPEE, BLOCKED, MOVING on a new line after each move are the only permitted responses. The last line is GOLD = number of gold squares found, TRAPS = number of traps hit.
""")
    print("=== TREASURE HUNT ===")
    print("""
Welcome to Treasure Hunt!

The game is played on a 10 by 10 grid. Every square has a coordinate made up
of an X value (column) and a Y value (row), both ranging from 1 to 10.
The bottom-left corner is (1,1) and the top-right corner is (10,10).

Moving changes your position like this:
  RIGHT  increases X by 1  (moves you east,  e.g. (3,5) -> (4,5))
  LEFT   decreases X by 1  (moves you west,  e.g. (3,5) -> (2,5))
  UP     increases Y by 1  (moves you north, e.g. (3,5) -> (3,6))
  DOWN   decreases Y by 1  (moves you south, e.g. (3,5) -> (3,4))

If a move would take you off the edge of the board it will be BLOCKED
and you will stay where you are.

The board has been randomly filled with:
  - 20 TRAPS  - landing on one gives you OUCH
  - 10 GOLD   - landing on one gives you YIPEE
  - The remaining 70 squares are empty and give you OK
  -  If you land on empty squares twice in a row, it gives you Moving
          
Once you land on a trap or gold square it disappears, so if you visit
the same square again it will just be OK.

The locations of all traps and gold squares are shown below. The board is
randomly generated each game so the positions will be different every time
you play.

You enter your starting square and your full list of moves all at once,
then watch the results play out step by step. For example:
  5,5,left,up,left,up,up,right,down

Or enter R,<number> to let the game pick a random start and generate that
many random moves for you. For example:
  R,30

At the end you will see a count of how many gold squares and traps you hit.

Good luck!
""")
    print("TRAP locations:")
    print(", ".join(f"({x},{y})" for x, y in sorted(traps)))
    print("\nGOLD locations:")
    print(", ".join(f"({x},{y})" for x, y in sorted(gold)))
    print()

# ---------------------------------------------------------------------------
# Input parsing
# ---------------------------------------------------------------------------

def get_input():
    print("Enter your starting square and moves.")
    print("Format: x,y,direction,direction,...")
    print("Directions: up, down, left, right")
    print("Example: 5,5,left,up,right,down")
    print()
    print("Or enter R,<number> for a random start and random moves.")
    print("Example: R,30")
    print()
    raw   = input("Your path: ").strip()
    parts = [p.strip().lower() for p in raw.split(",")]

    if parts[0] == "r":
        try:
            num_steps = int(parts[1])
        except (ValueError, IndexError):
            print("Invalid random format. Use R,<number> e.g. R,30")
            return None, None
        start_x    = random.randint(1, 10)
        start_y    = random.randint(1, 10)
        directions = ["up", "down", "left", "right"]
        moves      = [random.choice(directions) for _ in range(num_steps)]
        print(f"\nRandom start: ({start_x},{start_y})")
        print(f"Random moves: {','.join(moves)}")
        print()
        return (start_x, start_y), moves

    try:
        start_x = int(parts[0])
        start_y = int(parts[1])
    except (ValueError, IndexError):
        print("Invalid starting position.")
        return None, None

    moves = parts[2:]
    return (start_x, start_y), moves

# ---------------------------------------------------------------------------
# Core game engine  (returns responses list + counts, prints nothing)
# ---------------------------------------------------------------------------

DIRECTION_MAP = {
    "up":    (0,  1),
    "down":  (0, -1),
    "left":  (-1, 0),
    "right": (1,  0),
}

def run_game(start, moves, traps, gold, silent=False):
    """Play through the game.  Returns (responses, gold_count, trap_count).
    If silent=False the responses are printed as well."""
    x, y       = start
    gold_count = 0
    trap_count = 0
    responses  = []

    def visit(pos):
        nonlocal gold_count, trap_count
        if pos in gold:
            r = "YIPEE"
            gold_count += 1
            gold.discard(pos)
        elif pos in traps:
            r = "OUCH"
            trap_count += 1
            traps.discard(pos)
        else:
            r = "OK"
            # If the previous response was also "OK", change this one
            if responses and responses[-1] == "OK":
                r = "Moving"

        responses.append(r)
        if not silent:
            print(r)

    visit((x, y))

    for move in moves:
        if move not in DIRECTION_MAP:
            if not silent:
                print(f"Unknown move '{move}', skipping.")
            continue
        dx, dy = DIRECTION_MAP[move]
        nx, ny = x + dx, y + dy
        if not (1 <= nx <= 10 and 1 <= ny <= 10):
            responses.append("BLOCKED")
            if not silent:
                print("BLOCKED")
            continue
        x, y = nx, ny
        visit((x, y))

    summary = f"\nGOLD = {gold_count}, TRAP = {trap_count}"
    if not silent:
        print(summary)

    return responses, gold_count, trap_count

# ---------------------------------------------------------------------------
# Experiment mode
# ---------------------------------------------------------------------------

def run_experiment():
    print("\n=== EXPERIMENT MODE ===\n")
    try:
        num_tests  = int(input("Number of tests:    ").strip())
        seq_length = int(input("Moves per sequence: ").strip())
    except ValueError:
        print("Invalid input – all values must be whole numbers.")
        return

    print(f"\nRunning {num_tests} tests × {seq_length} moves each...\n")

    experiment_data = []

    for test_num in range(1, num_tests + 1):
        org_traps, org_gold = generate_board()
        traps = org_traps.copy()
        gold  = org_gold.copy()


        # Generate random path
        start_x    = random.randint(1, 10)
        start_y    = random.randint(1, 10)
        directions = ["up", "down", "left", "right"]
        moves      = [random.choice(directions) for _ in range(seq_length)]

        responses, gold_count, trap_count = run_game(
            (start_x, start_y), moves, traps, gold, silent=True
        )

        sequence_str = f"{start_x},{start_y}," + ",".join(moves)

        experiment_data.append({
            "test":       test_num,
            "board": {
                "traps": [{"x": x, "y": y} for x, y in sorted(org_traps)],
                "gold":  [{"x": x, "y": y} for x, y in sorted(org_gold)],
            },
            "sequence":   sequence_str,
            "start":      {"x": start_x, "y": start_y},
            "moves":      moves,
            "responses":  responses,
            "gold_found": gold_count,
            "traps_hit":  trap_count,
        })

        print(f"  Test {test_num:>3}/{num_tests}: "
              f"start=({start_x},{start_y})  "
              f"GOLD={gold_count}  TRAPS={trap_count}")

    print(f"\nExperiment complete. {num_tests} tests generated.")

    # Save prompt
    print()
    save = input("Save results to a JSON file? (yes/no): ").strip().lower()
    if save in ("yes", "y"):
        filename = input("Enter filename (without .json): ").strip()
        if not filename:
            filename = "experiment_results"
        filepath = f"{filename}.json"
        with open(filepath, "w") as f:
            json.dump(experiment_data, f, indent=2)
        print(f"Saved to {filepath}")
    else:
        print("Results not saved.")

# ---------------------------------------------------------------------------
# Interactive play mode
# ---------------------------------------------------------------------------

def run_interactive():
    original_traps, original_gold = generate_board()
    print_board_info(original_traps, original_gold)

    first_game = True
    while True:
        if not first_game:
            print("Same board, traps and gold reset to their original positions.")
            print()

        traps = set(original_traps)
        gold  = set(original_gold)

        start, moves = get_input()
        if start is None:
            return
        print()
        run_game(start, moves, traps, gold, silent=False)

        first_game = False
        print()
        choice = input("Play again on the same board? (yes/no): ").strip().lower()
        if choice not in ("yes", "y"):
            print("Thanks for playing. Goodbye!")
            break
        print()

# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    print("=== TREASURE HUNT ===\n")
    print("1. Play the game")
    print("2. Run an experiment (generate data set)")
    print()
    choice = input("Choose an option (1 or 2): ").strip()
    if choice == "2":
        run_experiment()
    else:
        run_interactive()

if __name__ == "__main__":
    main()
