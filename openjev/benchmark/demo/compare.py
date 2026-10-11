#!/usr/bin/env python3

import json
import re
import subprocess
import sys
import time
import urllib.request


MODEL = "qwen3:14b"
OLLAMA_URL = "http://127.0.0.1:11434/api/generate"


# ============================================================
# NORMAL OLLAMA LLM
# ============================================================

def normal_llm(text):

    prompt = f"""
You are a customer-support assistant.

Read the customer message below and respond naturally.
Explain what the customer needs and what action should be taken.

Customer message:
{text}
""".strip()

    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
    }

    request = urllib.request.Request(
        OLLAMA_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    start = time.perf_counter()

    with urllib.request.urlopen(request) as response:
        data = json.loads(response.read().decode("utf-8"))

    latency = time.perf_counter() - start

    return data, latency


# ============================================================
# OPENJEV + OLLAMA
# ============================================================

def openjev(text):

    command = [
        "openjev-easy",
        "--backend",
        "ollama",
        "--model",
        MODEL,
        "--once",
        text,
    ]

    start = time.perf_counter()

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
    )

    latency = time.perf_counter() - start

    if result.returncode != 0:
        raise RuntimeError(
            result.stderr.strip()
            or result.stdout.strip()
        )

    return result.stdout, latency


# ============================================================
# PARSE OPENJEV
# ============================================================

def parse_openjev(output):

    result = {
        "intent": None,
        "intent_confidence": None,
        "urgent_yes": None,
        "urgent_no": None,
        "sentiment_score": None,
    }

    lines = output.splitlines()

    # --------------------------------------------------------
    # Intent
    # --------------------------------------------------------

    for i, line in enumerate(lines):

        match = re.search(
            r"->\s*choice\s*=\s*([A-Za-z0-9_-]+)",
            line,
            re.IGNORECASE,
        )

        if match:

            result["intent"] = match.group(1)

            for candidate in lines[i:i + 4]:

                confidence = re.search(
                    r"confidence\s*[=:]\s*([0-9.]+)",
                    candidate,
                    re.IGNORECASE,
                )

                if confidence:

                    value = float(confidence.group(1))

                    # CLI may display either 0.95 or 95.00%
                    if value <= 1:
                        value *= 100

                    result["intent_confidence"] = value

    # --------------------------------------------------------
    # Urgency
    # --------------------------------------------------------

    for i, line in enumerate(lines):

        if line.strip().lower() == "urgent":

            for candidate in lines[i + 1:i + 8]:

                yes = re.search(
                    r"\bYes\b.*?([0-9.]+)%",
                    candidate,
                    re.IGNORECASE,
                )

                no = re.search(
                    r"\bNo\b.*?([0-9.]+)%",
                    candidate,
                    re.IGNORECASE,
                )

                if yes:
                    result["urgent_yes"] = float(
                        yes.group(1)
                    )

                if no:
                    result["urgent_no"] = float(
                        no.group(1)
                    )

    # --------------------------------------------------------
    # Sentiment score
    # --------------------------------------------------------

    for line in lines:

        match = re.search(
            r"->\s*score\s*=\s*([0-9.]+)",
            line,
            re.IGNORECASE,
        )

        if match:

            result["sentiment_score"] = float(
                match.group(1)
            )

    return result


# ============================================================
# DISPLAY
# ============================================================

def show_openjev(raw, parsed, latency):

    print()
    print("OPENJEV DECISION")
    print("-" * 72)

    print()

    print("Intent")

    if parsed["intent"]:
        print(
            f"  -> {parsed['intent']}"
        )

    if parsed["intent_confidence"] is not None:
        print(
            f"     confidence: "
            f"{parsed['intent_confidence']:.2f}%"
        )

    print()

    print("Urgency")

    if parsed["urgent_yes"] is not None:
        print(
            f"  Yes: {parsed['urgent_yes']:.2f}%"
        )

    if parsed["urgent_no"] is not None:
        print(
            f"  No : {parsed['urgent_no']:.2f}%"
        )

    print()

    if parsed["sentiment_score"] is not None:
        print(
            f"Sentiment score: "
            f"{parsed['sentiment_score']:.4f}"
        )

    print()

    print(
        f"Latency: {latency:.3f} seconds"
    )

    print()

    print("Raw OpenJev output")
    print("-" * 72)
    print(raw.strip())


# ============================================================
# MAIN
# ============================================================

def main():

    if len(sys.argv) > 1:

        text = " ".join(sys.argv[1:])

    else:

        print()
        print("=" * 72)
        print(" OpenJev vs Normal LLM")
        print("=" * 72)
        print()

        text = input("Message: ").strip()

        if not text:

            text = (
                "The server has been down for two hours and "
                "customers are unable to place orders. "
                "Please fix this immediately."
            )

    # --------------------------------------------------------
    # Input
    # --------------------------------------------------------

    print()
    print("=" * 72)
    print("INPUT")
    print("=" * 72)
    print()
    print(text)

    # --------------------------------------------------------
    # Normal LLM
    # --------------------------------------------------------

    print()
    print("=" * 72)
    print("1. NORMAL LLM")
    print("=" * 72)
    print()

    try:

        data, latency = normal_llm(text)

        print(
            data.get(
                "response",
                "(no response)"
            ).strip()
        )

        print()
        print(
            f"Latency: {latency:.3f} seconds"
        )

        if "prompt_eval_count" in data:
            print(
                f"Input tokens: "
                f"{data['prompt_eval_count']}"
            )

        if "eval_count" in data:
            print(
                f"Output tokens: "
                f"{data['eval_count']}"
            )

    except Exception as exc:

        print("ERROR:")
        print(exc)

    # --------------------------------------------------------
    # OpenJev
    # --------------------------------------------------------

    print()
    print("=" * 72)
    print("2. OPENJEV")
    print("=" * 72)

    try:

        raw, latency = openjev(text)

        parsed = parse_openjev(raw)

        show_openjev(
            raw,
            parsed,
            latency,
        )

    except Exception as exc:

        print("ERROR:")
        print(exc)

    # --------------------------------------------------------
    # Explanation
    # --------------------------------------------------------

    print()
    print("=" * 72)
    print("THE DIFFERENCE")
    print("=" * 72)
    print()

    print("NORMAL LLM")
    print("  Generates a natural-language response.")
    print("  Your application has to interpret that response.")

    print()

    print("OPENJEV")
    print("  Produces structured decisions.")
    print("  Intent  -> Choice")
    print("  Urgency -> Noul")
    print("  Sentiment -> Score")

    print()
    print("=" * 72)


if __name__ == "__main__":
    main()
