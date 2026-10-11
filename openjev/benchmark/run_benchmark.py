import json
import csv
import subprocess
import time
import re
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
SCENARIOS_FILE = BASE_DIR / "scenarios.json"
RESULTS_DIR = BASE_DIR / "results"

RESULTS_DIR.mkdir(exist_ok=True)


def run_openjev(text):
    command = [
        "openjev-easy",
        "--backend",
        "ollama",
        "--model",
        "qwen3:0.6b",
        "--once",
        text,
    ]

    start = time.perf_counter()

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )

    elapsed = time.perf_counter() - start

    return {
        "stdout": result.stdout,
        "stderr": result.stderr,
        "returncode": result.returncode,
        "latency_seconds": elapsed,
    }


def parse_output(output):

    result = {
        "intent": None,
        "intent_confidence": None,
        "urgent": None,
        "urgent_yes_probability": None,
        "sentiment": None,
    }

    lines = output.splitlines()

    # ------------------------------------------------------------
    # CHOICE
    #
    # Example:
    # -> choice = question
    #    confidence = 100.00%
    # ------------------------------------------------------------

    for i, line in enumerate(lines):

        match = re.search(
            r"->\s*choice\s*=\s*(\w+)",
            line,
            re.IGNORECASE,
        )

        if match:
            result["intent"] = match.group(1).lower()

            # Look at the next few lines for confidence
            for next_line in lines[i + 1:i + 4]:

                conf = re.search(
                    r"confidence\s*=\s*([0-9.]+)%",
                    next_line,
                    re.IGNORECASE,
                )

                if conf:
                    result["intent_confidence"] = (
                        float(conf.group(1)) / 100.0
                    )

            break

    # ------------------------------------------------------------
    # NOUL
    #
    # Example:
    #
    # urgent
    #   Yes 67.10%
    #   No  32.90%
    # ------------------------------------------------------------

    for i, line in enumerate(lines):

        if line.strip().lower() == "urgent":

            for next_line in lines[i + 1:i + 5]:

                yes_match = re.search(
                    r"Yes\s+([0-9.]+)%",
                    next_line,
                    re.IGNORECASE,
                )

                if yes_match:
                    result["urgent_yes_probability"] = (
                        float(yes_match.group(1)) / 100.0
                    )

                    result["urgent"] = (
                        result["urgent_yes_probability"] >= 0.5
                    )

                    break

    # ------------------------------------------------------------
    # SENTIMENT
    #
    # Current OpenJev uses Score for sentiment.
    #
    # We don't convert it to a class yet.
    # We'll handle the score properly in v2.
    # ------------------------------------------------------------

    return result


def main():

    print("=" * 70)
    print("OPENJEV BENCHMARK")
    print("Backend: ollama")
    print("Model:   qwen3:0.6b")
    print("=" * 70)
    print()

    with open(SCENARIOS_FILE, "r", encoding="utf-8") as f:
        scenarios = json.load(f)

    results = []

    for number, scenario in enumerate(scenarios, start=1):

        print(
            f"[{number:02d}/{len(scenarios)}] "
            f"{scenario['id']}: "
            f"{scenario['text']}"
        )

        response = run_openjev(scenario["text"])

        if response["returncode"] != 0:

            print("  ERROR")
            print(response["stderr"])

            results.append({
                "id": scenario["id"],
                "category": scenario["category"],
                "text": scenario["text"],
                "expected": scenario["expected"],
                "actual": {},
                "status": "ERROR",
                "latency_seconds": response["latency_seconds"],
                "raw_output": response["stdout"],
            })

            continue

        actual = parse_output(response["stdout"])
        expected = scenario["expected"]

        intent_ok = (
            actual["intent"] == expected["intent"]
        )

        urgent_ok = (
            actual["urgent"] == expected["urgent"]
        )

        # We don't score sentiment yet.
        # Score requires handling the probability distribution.
        sentiment_ok = None

        all_ok = intent_ok and urgent_ok

        status = "PASS" if all_ok else "FAIL"

        print(
            f"  intent:    "
            f"{actual['intent']} "
            f"({'OK' if intent_ok else 'FAIL'})"
        )

        print(
            f"  confidence: "
            f"{actual['intent_confidence']}"
        )

        print(
            f"  urgent:    "
            f"{actual['urgent']} "
            f"({'OK' if urgent_ok else 'FAIL'})"
        )

        print(
            f"  urgent P(yes): "
            f"{actual['urgent_yes_probability']}"
        )

        print(
            f"  RESULT:    {status}"
        )

        print(
            f"  latency:   "
            f"{response['latency_seconds']:.2f}s"
        )

        print()

        results.append({
            "id": scenario["id"],
            "category": scenario["category"],
            "text": scenario["text"],
            "expected": expected,
            "actual": actual,
            "intent_correct": intent_ok,
            "urgent_correct": urgent_ok,
            "sentiment_correct": sentiment_ok,
            "status": status,
            "latency_seconds": response["latency_seconds"],
            "raw_output": response["stdout"],
        })

    # ------------------------------------------------------------
    # SAVE JSON
    # ------------------------------------------------------------

    json_file = RESULTS_DIR / "results.json"

    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(
            results,
            f,
            indent=2,
            ensure_ascii=False,
        )

    # ------------------------------------------------------------
    # SAVE CSV
    # ------------------------------------------------------------

    csv_file = RESULTS_DIR / "results.csv"

    with open(
        csv_file,
        "w",
        encoding="utf-8",
        newline="",
    ) as f:

        writer = csv.writer(f)

        writer.writerow([
            "id",
            "category",
            "expected_intent",
            "actual_intent",
            "intent_correct",
            "intent_confidence",
            "expected_urgent",
            "actual_urgent",
            "urgent_correct",
            "urgent_yes_probability",
            "status",
            "latency_seconds",
        ])

        for r in results:

            writer.writerow([
                r["id"],
                r["category"],
                r["expected"]["intent"],
                r["actual"].get("intent"),
                r["intent_correct"],
                r["actual"].get(
                    "intent_confidence"
                ),
                r["expected"]["urgent"],
                r["actual"].get("urgent"),
                r["urgent_correct"],
                r["actual"].get(
                    "urgent_yes_probability"
                ),
                r["status"],
                f"{r['latency_seconds']:.4f}",
            ])

    # ------------------------------------------------------------
    # SUMMARY
    # ------------------------------------------------------------

    valid = [
        r for r in results
        if r["status"] != "ERROR"
    ]

    if not valid:
        print("No successful tests.")
        return

    intent_accuracy = (
        sum(r["intent_correct"] for r in valid)
        / len(valid)
    )

    urgent_accuracy = (
        sum(r["urgent_correct"] for r in valid)
        / len(valid)
    )

    avg_latency = (
        sum(r["latency_seconds"] for r in valid)
        / len(valid)
    )

    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)

    print(
        f"Scenarios:        {len(valid)}"
    )

    print(
        f"Intent accuracy:  "
        f"{intent_accuracy * 100:.1f}%"
    )

    print(
        f"Urgency accuracy: "
        f"{urgent_accuracy * 100:.1f}%"
    )

    print(
        f"Average latency:  "
        f"{avg_latency:.2f}s"
    )

    print()

    print(f"JSON: {json_file}")
    print(f"CSV:  {csv_file}")


if __name__ == "__main__":
    main()
