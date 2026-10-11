#!/usr/bin/env python3

import json
import re
import subprocess
import sys
import time
import urllib.request


#MODEL = "qwen3:0.6b"
MODEL = "qwen3:14b"
OLLAMA_URL = "http://127.0.0.1:11434/api/generate"


# ------------------------------------------------------------
# Normal LLM
# ------------------------------------------------------------

def ask_normal_llm(text):
    prompt = f"""
You are a helpful customer-support assistant.

Read the following customer message and respond naturally.
Explain what you think the customer needs and what should
be done.

Customer message:
{text}
""".strip()

    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
    }

    data = json.dumps(payload).encode("utf-8")

    request = urllib.request.Request(
        OLLAMA_URL,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    start = time.perf_counter()

    with urllib.request.urlopen(request) as response:
        result = json.loads(response.read().decode("utf-8"))

    latency = time.perf_counter() - start

    return result.get("response", "").strip(), latency


# ------------------------------------------------------------
# OpenJev
# ------------------------------------------------------------

def ask_openjev(text):
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

    output = result.stdout

    if result.returncode != 0:
        raise RuntimeError(
            "OpenJev failed:\n\n" + result.stderr
        )

    return parse_openjev(output), latency, output


# ------------------------------------------------------------
# Parse OpenJev CLI output
# ------------------------------------------------------------

def parse_openjev(output):
    result = {
        "intent": None,
        "intent_confidence": None,
        "urgent_yes": None,
        "urgent_no": None,
        "raw": output,
    }

    lines = output.splitlines()

    # -------------------------
    # Choice / intent
    # -------------------------

    for i, line in enumerate(lines):

        match = re.search(
            r"->\s*choice\s*=\s*([A-Za-z0-9_-]+)",
            line,
            re.IGNORECASE,
        )

        if match:
            result["intent"] = match.group(1)

            # Search nearby lines for confidence.
            nearby = lines[i:i + 3]

            for candidate in nearby:
                conf = re.search(
                    r"confidence\s*=\s*([0-9.]+)",
                    candidate,
                    re.IGNORECASE,
                )

                if conf:
                    result["intent_confidence"] = float(
                        conf.group(1)
                    )

    # -------------------------
    # Noul / urgency
    # -------------------------

    for i, line in enumerate(lines):

        if line.strip().lower() == "urgent":

            for candidate in lines[i + 1:i + 6]:

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

    return result


# ------------------------------------------------------------
# Pretty printing
# ------------------------------------------------------------

def print_bar(label, value, width=35):

    if value is None:
        print(f"  {label:<12} unavailable")
        return

    blocks = int((value / 100) * width)

    print(
        f"  {label:<12} "
        f"{'█' * blocks}"
        f"{' ' * (width - blocks)} "
        f"{value:6.2f}%"
    )


def print_openjev(result):

    print("OPENJEV")
    print("-" * 60)

    print()
    print("Intent:")

    if result["intent"]:
        print(
            f"  -> {result['intent']}"
            + (
                f"  confidence="
                f"{result['intent_confidence']:.2f}%"
                if result["intent_confidence"] is not None
                else ""
            )
        )
    else:
        print("  -> unavailable")

    print()
    print("Urgency:")

    print_bar("Yes", result["urgent_yes"])
    print_bar("No", result["urgent_no"])

    print()
    print("Raw OpenJev output:")
    print()

    # Show only the useful section of the CLI result.
    print(result["raw"].strip())


# ------------------------------------------------------------
# Main demo
# ------------------------------------------------------------

def main():

    if len(sys.argv) > 1:
        text = " ".join(sys.argv[1:])
    else:
        print()
        print("=" * 60)
        print(" OpenJev vs Normal LLM")
        print("=" * 60)
        print()
        print("Enter a customer message.")
        print("Press ENTER on an empty line to use the example.")
        print()

        text = input("Message: ").strip()

        if not text:
            text = (
                "The server has been down for two hours and "
                "customers are unable to place orders. "
                "Please fix this immediately."
            )

    print()
    print("=" * 60)
    print("USER MESSAGE")
    print("=" * 60)
    print()
    print(text)

    # --------------------------------------------------------
    # Normal LLM
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("1. NORMAL LLM")
    print("=" * 60)
    print()

    try:
        normal_answer, normal_latency = ask_normal_llm(text)

        print(normal_answer)

        print()
        print(
            f"Latency: {normal_latency:.3f} seconds"
        )

    except Exception as exc:
        print("Normal LLM error:")
        print(exc)
        normal_latency = None

    # --------------------------------------------------------
    # OpenJev
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("2. OPENJEV")
    print("=" * 60)
    print()

    try:
        openjev_result, openjev_latency, raw = ask_openjev(text)

        print_openjev(openjev_result)

        print()
        print(
            f"Latency: {openjev_latency:.3f} seconds"
        )

    except Exception as exc:
        print("OpenJev error:")
        print(exc)
        openjev_latency = None

    # --------------------------------------------------------
    # Explanation
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("WHAT IS DIFFERENT?")
    print("=" * 60)
    print()

    print(
        "Normal LLM:"
    )
    print(
        "  -> generates natural-language tokens"
    )
    print(
        "  -> produces an explanation / answer"
    )
    print(
        "  -> application must interpret the answer"
    )

    print()

    print(
        "OpenJev:"
    )
    print(
        "  -> does not generate a normal answer"
    )
    print(
        "  -> reads the model's decision probabilities"
    )
    print(
        "  -> returns structured decisions"
    )
    print(
        "  -> application gets machine-readable values"
    )

    print()
    print("=" * 60)
    print()


if __name__ == "__main__":
    main()
