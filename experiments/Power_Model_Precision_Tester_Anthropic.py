"""
Power_Model_Tester.py
=====================
Loads a Treasure Hunt experiment JSON file and runs it against one or
more OpenAI models, producing per-model results JSON files and a
combined CSV comparison file in multi-model mode.

Experiment JSON structure
-------------------------
Each test is a flat object — one board, one start position, one move
sequence, one set of ground-truth responses.  No games layer.

[
  {
    "test": 1,
    "board": { "gold": [{"x":1,"y":6}, ...], "traps": [{"x":1,"y":1}, ...] },
    "start": {"x": 5, "y": 2},
    "moves": ["right", "up", "left", ...],
    "responses": [[ "OK", [x0, y0] ], [ "OUCH", [x1, y1] ], [ "YIPEE", [x2, y2] ], ...],
    "gold_found": 1,
    "traps_hit":  1
  },
  ...
]

Model response (per test)
-------------------------
{"responses": [{"move": 0, "x": 0, "y": 0, "text": "OK"}, ...], "gold": 1, "traps": 1}

Modes
-----
Single model : uses the "model" key in config.json
Multi-model  : iterates through all "model-1", "model-2", ... keys in config.json

Test file mode
--------------
Single file  : choose from list
Batch        : run all experiment files in the current directory

File naming
-----------
Results JSON : results_{model}_{test_name}_{nt}_{ns}_{timestamp}.json
  where nt = number of tests, ns = moves per test
CSV summary  : comparison_{test_name}_{nt}_{ns}_{timestamp}.csv

Requirements:
    pip install openai
    config.json in the same directory as this script.
"""

import json
import os
import sys
import re
import csv
import glob
from datetime import datetime

try:
    from openai import OpenAI
except ImportError:
    sys.exit("openai package not found.  Run: pip install openai")


from anthropic import AnthropicFoundry


# ---------------------------------------------------------------------------
# Config + file loading
# ---------------------------------------------------------------------------

def load_config():
    script_dir  = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, "config.json")
    if not os.path.exists(config_path):
        sys.exit(f"config.json not found at {config_path}")
    with open(config_path) as f:
        return json.load(f)


def get_models(config, multi_model):
    """
    Return a list of (label, model_string) tuples.
    Single mode : [("model", "gpt-4o")]
    Multi mode  : [("model-1", "gpt-4o"), ("model-2", "gpt-4-turbo"), ...]
    """
    if not multi_model:
        return [("model", config.get("model", "gpt-4o"))]
    models = []
    for key in sorted(config.keys()):
        if re.match(r"^model-\d+$", key):
            models.append((key, config[key]))
    if not models:
        print("No model-N entries found in config.json, falling back to single model.")
        return [("model", config.get("model", "gpt-4o"))]
    return models


def get_experiment_files():
    """Return sorted list of all experiment JSON files in the current directory."""
    json_files = sorted(glob.glob("*.json"))
    return [f for f in json_files
            if f != "config.json"
            and not f.startswith("results_")
            and not f.startswith("comparison_")]


def choose_json_file(json_files):
    print("\nAvailable experiment files:")
    for i, fname in enumerate(json_files, 1):
        print(f"  {i}. {fname}")
    print()
    while True:
        try:
            choice = int(input("Select a file by number: ").strip())
            if 1 <= choice <= len(json_files):
                return json_files[choice - 1]
        except ValueError:
            pass
        print("Invalid choice, try again.")


def load_experiment(filepath):
    with open(filepath) as f:
        return json.load(f)


def parse_test_params(filename, experiment):
    """
    Extract (test_name, nt, ns) from filename like test_20_50.json,
    or derive them from the experiment data if the name does not match.
    nt = number of tests, ns = moves per test.
    """
    base = os.path.splitext(os.path.basename(filename))[0]
    m    = re.match(r"^(.+?)_(\d+)_(\d+)$", base)
    if m:
        return m.group(1), int(m.group(2)), int(m.group(3))
    # Derive from data
    nt = len(experiment)
    ns = len(experiment[0]["moves"]) if nt else 0
    return base, nt, ns


# ---------------------------------------------------------------------------
# Prompt builder
# ---------------------------------------------------------------------------

def format_coord_list(squares):
    return ", ".join(f"({s['x']},{s['y']})" for s in squares)


def build_prompt(config, test_entry):
    board    = test_entry["board"]
    gold_str = format_coord_list(board["gold"])
    trap_str = format_coord_list(board["traps"])
    sx       = test_entry["start"]["x"]
    sy       = test_entry["start"]["y"]
    moves    = ", ".join(test_entry["moves"])
    game_str = f"start=({sx},{sy}), moves: {moves}"

    output_template = json.dumps({
        "responses": [
                    {"move": 0, "x": 0, "y": 0, "text": "OK"},
                    {"move": 1, "x": 1, "y": 0, "text": "YIPEE"}
                ],
                "gold": 1,
                "traps": 0
        
    }, indent=2)

    prompt_a = config["Prompt_A"]
    prompt_b = config["Prompt_B"]
    prompt_c = config["Prompt_C"]
    
    Prompt_str = (
        f"{prompt_a}\n{gold_str}\n\n"
        f"TRAP squares:\n{trap_str}\n\n"
        f"{prompt_b}\n\n"
        f"\n{game_str}\n\n"
        f"{prompt_c}"
    )
    # print (f"\nGenerated prompt for test {test_entry['test']}:\n{'-'*40}\n{Prompt_str}\n{'-'*40}")
    return Prompt_str
    

# ---------------------------------------------------------------------------
# OpenAI — single call per test
# ---------------------------------------------------------------------------

def run_test(client, model_str, config, test_entry):
    prompt = build_prompt(config, test_entry)


    system_prompt = (
        "You are a precise Treasure Hunt game engine. "
        "Follow the rules exactly. "
        "Return only valid JSON. "
        "Never add text outside the JSON."
    )

    messages = [
        {
            "role": "user",
            "content": prompt
        }
    ]


    response   = client.messages.create(
        model=model_str,
        system=system_prompt,
        messages=messages,
        temperature=1,
        max_tokens=1024
    )

    reply_text = response.content[0].text.strip()

        

    usage   = response.usage

    prompt_tokens = response.usage.input_tokens if usage else None
    completion_tokens = response.usage.output_tokens if usage else None

    metrics = {
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": (prompt_tokens + completion_tokens) if usage else None,
        "model": response.model,
        "finish_reason": response.stop_reason,
    }

    # Strip markdown fences if the model wrapped its JSON
    clean = reply_text
    if clean.startswith("```"):
        clean = "\n".join(clean.split("\n")[1:])
    if clean.endswith("```"):
        clean = clean[: clean.rfind("```")]
    clean = clean.strip()

    try:
        return json.loads(clean), metrics
    except json.JSONDecodeError:
        print(f"    WARNING: Could not parse model response as JSON:\n    {reply_text[:300]}")
        return None, metrics


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

def score_test(test_entry, model_response):
    ground_truth = test_entry["responses"]
    total = len(ground_truth)

    model_items = model_response.get("responses", []) if model_response else []

    correct = 0
    first_error = None

    #error tracking
    pos_errors = 0
    text_errors = 0
    both_errors = 0

    for i, expected in enumerate(ground_truth):
        expected_text = str(expected[0]).strip().upper()
        expected_pos  = tuple(expected[1])

        if i < len(model_items) and isinstance(model_items[i], dict):
            actual_text = str(model_items[i].get("text", "")).strip().upper()
            actual_pos  = (model_items[i].get("x"), model_items[i].get("y"))
        else:
            actual_text = ""
            actual_pos = None

        if actual_text == expected_text and actual_pos == expected_pos:
            correct += 1
        else:
            if actual_text != expected_text and actual_pos != expected_pos:
                both_errors += 1
            elif actual_text != expected_text:
                text_errors += 1
            elif actual_pos != expected_pos:
                pos_errors += 1

            if first_error is None:
                first_error = i

    incorrect = total - correct

    return {
        "test": test_entry["test"],
        "moves_in_sequence": total,
        "correct": correct,
        "incorrect": incorrect,
        "accuracy_pct": round(correct / total * 100, 1) if total else 0,
        "passed": incorrect == 0,
        "first_error_move": first_error,
        "pos_errors": pos_errors,
        "text_errors": text_errors,
        "both_errors": both_errors,
    }

# ---------------------------------------------------------------------------
# Run one model against the full experiment
# ---------------------------------------------------------------------------

def run_model(client, model_label, model_str, config, experiment,
              input_file, test_name, nt, ns):

    print(f"\n{'='*60}")
    print(f"  Model: {model_str}  ({model_label})")
    print(f"{'='*60}")

    all_results             = []
    grand_moves             = 0
    grand_correct           = 0
    grand_failed_tests      = 0
    grand_prompt_tokens     = 0
    grand_completion_tokens = 0
    grand_total_tokens      = 0

    #error aggregation
    grand_pos_errors  = 0
    grand_text_errors = 0
    grand_both_errors = 0

    all_first_errors   = []
    all_failure_counts = []

    num_tests = len(experiment)

    for test_entry in experiment:
        test_num = test_entry["test"]
        print(f"\n  --- Test {test_num}/{num_tests} --- ", end="", flush=True)

        model_response, metrics = run_test(client, model_str, config, test_entry)

        # --- token tracking ---
        if metrics["prompt_tokens"] is not None:
            grand_prompt_tokens     += metrics["prompt_tokens"]
            grand_completion_tokens += metrics["completion_tokens"]
            grand_total_tokens      += metrics["total_tokens"]

        # --- failure case: invalid output ---
        if model_response is None:
            print(f"FAILED (parse error)  "
                  f"[tokens: {metrics['total_tokens']} | "
                  f"finish: {metrics['finish_reason']}]")

            grand_failed_tests += 1

            all_results.append({
                "test": test_num,
                "error": "parse error — no valid JSON returned",
                "metrics": metrics,
            })
            continue

        # --- scoring ---
        result = score_test(test_entry, model_response)
        result["metrics"] = metrics
        all_results.append(result)

        # --- totals ---
        grand_moves   += result["moves_in_sequence"]
        grand_correct += result["correct"]

        #accumulate error types
        grand_pos_errors  += result.get("pos_errors", 0)
        grand_text_errors += result.get("text_errors", 0)
        grand_both_errors += result.get("both_errors", 0)

        # --- failures ---
        if not result["passed"]:
            grand_failed_tests += 1
            all_failure_counts.append(result["incorrect"])

            if result["first_error_move"] is not None:
                all_first_errors.append(result["first_error_move"])

        # --- print ---
        status = "PASS" if result["passed"] else "FAIL"
        print(f"{status}  {result['correct']}/{result['moves_in_sequence']} correct "
              f"({result['accuracy_pct']}%)  "
              f"[tokens in:{metrics['prompt_tokens']} "
              f"out:{metrics['completion_tokens']} "
              f"finish:{metrics['finish_reason']}]")

        if result["first_error_move"] is not None:
            print(f"           First error at move {result['first_error_move']}")

    # -----------------------------
    # Final calculations
    # -----------------------------
    perfect_tests = num_tests - grand_failed_tests

    avg_first_error = (
        round(sum(all_first_errors) / len(all_first_errors), 2)
        if all_first_errors else None
    )

    avg_failure_count = (
        round(sum(all_failure_counts) / len(all_failure_counts), 2)
        if all_failure_counts else None
    )

    total_errors = grand_pos_errors + grand_text_errors + grand_both_errors

    # -----------------------------
    # Summary
    # -----------------------------
    summary = {
        "experiment_file": input_file,
        "model_label": model_label,
        "model": model_str,
        "temperature": 1,
        "run_timestamp": datetime.now().isoformat(),

        "total_tests": num_tests,
        "perfect_tests": perfect_tests,
        "failed_tests": grand_failed_tests,

        "grand_total_moves": grand_moves,
        "grand_correct": grand_correct,
        "grand_incorrect": grand_moves - grand_correct,
        "grand_accuracy": round(grand_correct / grand_moves * 100, 1) if grand_moves else 0,

        "avg_first_error_move": avg_first_error,
        "avg_failures_per_failed_test": avg_failure_count,

        #error analysis
        "grand_error_breakdown": {
            "position_errors": grand_pos_errors,
            "text_errors": grand_text_errors,
            "both_errors": grand_both_errors,

            "position_error_pct": round(grand_pos_errors / total_errors * 100, 1) if total_errors else 0,
            "text_error_pct": round(grand_text_errors / total_errors * 100, 1) if total_errors else 0,
            "both_error_pct": round(grand_both_errors / total_errors * 100, 1) if total_errors else 0,
        },

        "token_usage": {
            "total_prompt_tokens": grand_prompt_tokens,
            "total_completion_tokens": grand_completion_tokens,
            "total_tokens": grand_total_tokens,

            "avg_prompt_tokens": round(grand_prompt_tokens / num_tests, 1) if num_tests else 0,
            "avg_completion_tokens": round(grand_completion_tokens / num_tests, 1) if num_tests else 0,
            "avg_total_tokens": round(grand_total_tokens / num_tests, 1) if num_tests else 0,
        },

        "tests": all_results,
    }

    # -----------------------------
    # Console summary
    # -----------------------------
    print(f"\n  === {model_str}: {grand_correct}/{grand_moves} correct "
          f"({summary['grand_accuracy']}%) ===")
    print(f"      Perfect tests:              {perfect_tests}/{num_tests}")
    print(f"      Failed tests:               {grand_failed_tests}/{num_tests}")

    print("\n      Error breakdown:")
    print(f"         Position errors: {grand_pos_errors}")
    print(f"         Text errors:     {grand_text_errors}")
    print(f"         Both errors:     {grand_both_errors}")

    print(f"\n      Total tokens used:          {grand_total_tokens}")
    print(f"      Avg tokens/test:            {summary['token_usage']['avg_total_tokens']}")
    print(f"      Prompt tokens:              {grand_prompt_tokens}")
    print(f"      Completion tokens:          {grand_completion_tokens}")
    print(f"      Avg first error (move#):    {avg_first_error}")
    print(f"      Avg failures/failed test:   {avg_failure_count}")

    # -----------------------------
    # Save results
    # -----------------------------
    safe_model  = re.sub(r"[^\w\-]", "_", model_str)
    timestamp   = datetime.now().strftime("%Y%m%d_%H%M%S")
    result_file = f"results_{safe_model}_{test_name}_{nt}_{ns}_{timestamp}.json"

    with open(result_file, "w") as f:
        json.dump(summary, f, indent=2)

    print(f"\n  Results saved to {result_file}")

    return summary

# ---------------------------------------------------------------------------
# CSV comparison report
# ---------------------------------------------------------------------------

def write_csv(model_summaries, test_name, nt, ns):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_file  = f"comparison_{test_name}_{nt}_{ns}_{timestamp}.csv"

    headers = [
        "Model",
        "Correct", "Total Moves", "Accuracy %",
        "Perfect Tests", "Failed Tests", "Total Tests",

        #error breakdown values
        "Position Errors", "Text Errors", "Both Errors",
        "Pos Err %", "Text Err %", "Both Err %",

        "Total Tokens", "Avg Tokens/Test",
        "Prompt Tokens", "Completion Tokens",
        "Avg First Error (Move#)", "Avg Failures/Failed Test",
    ]

    with open(csv_file, "w", newline="") as f:
        writer = csv.writer(f)

        writer.writerow([f"TEST: {test_name}", f"NT: {nt}", f"NS: {ns}"])
        writer.writerow([])
        writer.writerow(headers)

        for s in model_summaries:
            tu = s["token_usage"]
            err = s.get("grand_error_breakdown", {})

            writer.writerow([
                s["model"],
                s["grand_correct"],
                s["grand_total_moves"],
                s["grand_accuracy"],
                s["perfect_tests"],
                s["failed_tests"],
                s["total_tests"],

                #error breakdown values
                err.get("position_errors", 0),
                err.get("text_errors", 0),
                err.get("both_errors", 0),
                err.get("position_error_pct", 0),
                err.get("text_error_pct", 0),
                err.get("both_error_pct", 0),

                tu["total_tokens"],
                tu["avg_total_tokens"],
                tu["total_prompt_tokens"],
                tu["total_completion_tokens"],

                s["avg_first_error_move"] if s["avg_first_error_move"] is not None else "N/A",
                s["avg_failures_per_failed_test"] if s["avg_failures_per_failed_test"] is not None else "N/A",
            ])

    print(f"\nCSV comparison saved to {csv_file}")
    return csv_file


# ---------------------------------------------------------------------------
# Single file runner
# ---------------------------------------------------------------------------

def run_single_file(client, config, input_file, models, multi_model):
    """Run all models against one experiment file."""
    experiment = load_experiment(input_file)
    test_name, nt, ns = parse_test_params(input_file, experiment)

    print(f"\nLoaded {nt} tests from '{input_file}'  (nt={nt}, ns={ns})")

    model_summaries = []
    for model_label, model_str in models:
        summary = run_model(
            client, model_label, model_str, config, experiment,
            input_file, test_name, nt, ns
        )
        model_summaries.append(summary)

    if multi_model and len(model_summaries) > 1:
        write_csv(model_summaries, test_name, nt, ns)

    return model_summaries


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("=== Treasure Hunt — AI Model Evaluator ===\n")

    config  = load_config()
    api_key = config.get("openai_api_key", "")
    if not api_key or api_key.startswith("sk-YOUR"):
        sys.exit("Please set a valid openai_api_key in config.json")

    # Model mode selection
    print("Model mode:")
    print("  1. Single model  (uses 'model' in config.json)")
    print("  2. Multi-model   (iterates through model-1, model-2, ... in config.json)")
    print()
    while True:
        mode = input("Select mode (1 or 2): ").strip()
        if mode in ("1", "2"):
            break
        print("Please enter 1 or 2.")

    multi_model = (mode == "2")
    models      = get_models(config, multi_model)

    if multi_model:
        print(f"\nModels to test ({len(models)}):")
        for label, mstr in models:
            print(f"  {label}: {mstr}")

    # Test file selection
    json_files = get_experiment_files()
    if not json_files:
        sys.exit("No experiment JSON files found in the current directory.")

    print("\nTest file mode:")
    print("  1. Single file  (choose from list)")
    print(f"  2. Batch        (run all {len(json_files)} experiment files in this directory)")
    print()
    while True:
        file_mode = input("Select test mode (1 or 2): ").strip()
        if file_mode in ("1", "2"):
            break
        print("Please enter 1 or 2.")

    if file_mode == "1":
        input_files = [choose_json_file(json_files)]
    else:
        input_files = json_files
        print(f"\nBatch mode — {len(input_files)} files to process:")
        for f in input_files:
            print(f"  {f}")


    endpoint = "https://foundry-claude-katy.services.ai.azure.com/anthropic/"

    client = AnthropicFoundry(
        api_key=api_key,
        base_url=endpoint
    )

    for i, input_file in enumerate(input_files, 1):
        if len(input_files) > 1:
            print(f"\n{'='*60}")
            print(f"  FILE {i}/{len(input_files)}: {input_file}")
            print(f"{'='*60}")
        run_single_file(client, config, input_file, models, multi_model)

    print("\nDone.")


if __name__ == "__main__":
    main()
