#!/usr/bin/env python3

import os
import shutil
import subprocess
import sys
import textwrap
import time


WIDTH = 78


def clear():
    os.system("clear" if os.name != "nt" else "cls")


def pause():
    input("\nPress ENTER to continue...")


def title(text):
    print()
    print("=" * WIDTH)
    print(f"{text:^{WIDTH}}")
    print("=" * WIDTH)
    print()


def section(text):
    print()
    print("-" * WIDTH)
    print(f" {text}")
    print("-" * WIDTH)
    print()


def bullet(text):
    print(f"  • {text}")


def paragraph(text):
    print(textwrap.fill(text, WIDTH - 4))
    print()


def show_box(lines):
    print("┌" + "─" * (WIDTH - 2) + "┐")
    for line in lines:
        print("│ " + line.center(WIDTH - 4) + " │")
    print("└" + "─" * (WIDTH - 2) + "┘")


def run_command(command):
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=10,
        )

        return result.returncode, result.stdout, result.stderr

    except Exception as exc:
        return 1, "", str(exc)


# ============================================================
# INTRO
# ============================================================

def intro():

    clear()

    title("OPENJEV — FROM LLM TO DECISION ENGINE")

    show_box([
        "Same small local LLM",
        "Different way of using it",
    ])

    print()

    print("This demo explains:")
    print()

    bullet("What is OpenJev?")
    bullet("What does Jev mean?")
    bullet("What is System 1?")
    bullet("What is System 2?")
    bullet("How is OpenJev different from a normal LLM?")
    bullet("How does the OpenJev comparison demo work?")
    bullet("Why probabilities matter?")
    bullet("Where should each approach be used?")

    pause()


# ============================================================
# WHAT IS JEV
# ============================================================

def what_is_jev():

    clear()

    title("1. WHAT IS JEV?")

    paragraph(
        "Jev is a decision-model concept associated with TypeSafe. "
        "Instead of primarily asking a model to generate a paragraph "
        "of text, the interface asks it typed questions and receives "
        "structured decisions with probabilities."
    )

    show_box([
        "Normal LLM",
        "Question → generated text",
        "",
        "Jev-style model",
        "Question → typed decision + probability",
    ])

    print()

    paragraph(
        "For example, instead of asking a model to explain whether "
        "a customer message is urgent, a decision model can answer "
        "a yes/no question directly."
    )

    print("Example:")
    print()
    print('  Message: "The production server is down. Fix it NOW."')
    print()
    print("  Question: Is this urgent?")
    print()
    print("  Answer:")
    print("      Yes:  97.8%")
    print("      No:    2.2%")

    pause()


# ============================================================
# WHAT IS OPENJEV
# ============================================================

def what_is_openjev():

    clear()

    title("2. WHAT IS OPENJEV?")

    paragraph(
        "OpenJev is an open-source implementation inspired by the "
        "Jev-style System One decision interface. It allows an open "
        "local language model to be used as a decision engine."
    )

    print("In our experiment:")
    print()

    show_box([
        "Qwen3 0.6B",
        "running locally through Ollama",
        "",
        "↓",
        "",
        "OpenJev",
        "",
        "↓",
        "",
        "structured decision",
    ])

    print()

    bullet("No cloud API is required.")
    bullet("The model runs on the local machine.")
    bullet("The application receives structured decisions.")
    bullet("OpenJev supports Choice, Noul and Score.")

    pause()


# ============================================================
# WHAT DOES JEV MEAN
# ============================================================

def what_jev_means():

    clear()

    title("3. WHAT DOES 'JEV' MEAN?")

    paragraph(
        "In this context, Jev is the name of the decision-model "
        "system/product. It should not be confused with the general "
        "psychology terms System 1 and System 2."
    )

    show_box([
        "Jev",
        "decision-model interface / product",
        "",
        "OpenJev",
        "open-source Jev-style implementation",
    ])

    print()

    paragraph(
        "OpenJev is not the original closed Jev model. It is an "
        "independent implementation that reproduces the style of "
        "typed decision interfaces using open models."
    )

    print("Important:")
    print()
    bullet("Jev ≠ OpenJev")
    bullet("OpenJev ≠ a copy of Jev's proprietary weights")
    bullet("OpenJev uses open models such as Qwen")

    pause()


# ============================================================
# SYSTEM 1
# ============================================================

def system_one():

    clear()

    title("4. WHAT IS SYSTEM 1?")

    paragraph(
        "The System 1 / System 2 terminology comes from Daniel "
        "Kahneman's framework for describing two broad modes of "
        "thinking."
    )

    show_box([
        "SYSTEM 1",
        "Fast • intuitive • automatic",
    ])

    print()

    print("Typical examples:")
    print()

    bullet("Recognizing a familiar pattern")
    bullet("Detecting an obvious sentiment")
    bullet("Routing a support ticket")
    bullet("Answering yes/no")
    bullet("Choosing one category")
    bullet("Detecting whether something appears urgent")

    print()

    paragraph(
        "The important idea for OpenJev is not that the model has "
        "a human brain or literally contains two biological systems. "
        "System One is a useful analogy for a fast bounded decision "
        "stage."
    )

    pause()


# ============================================================
# SYSTEM 2
# ============================================================

def system_two():

    clear()

    title("5. WHAT IS SYSTEM 2?")

    show_box([
        "SYSTEM 2",
        "Slower • deliberate • analytical",
    ])

    print()

    print("Typical examples:")
    print()

    bullet("Writing a detailed answer")
    bullet("Solving a multi-step problem")
    bullet("Planning")
    bullet("Comparing several complex alternatives")
    bullet("Writing code")
    bullet("Reasoning through unfamiliar information")

    print()

    paragraph(
        "A normal chat LLM is often used in a System-2-like role: "
        "it generates a sequence of tokens that can contain an "
        "explanation, reasoning, instructions or a complete answer."
    )

    print()
    print("This distinction is conceptual, not a claim that an LLM")
    print("literally contains two separate neural systems.")

    pause()


# ============================================================
# SYSTEM 1 VS SYSTEM 2
# ============================================================

def comparison():

    clear()

    title("6. SYSTEM 1 vs SYSTEM 2")

    print()
    print(f"{'SYSTEM 1':<38} {'SYSTEM 2':<38}")
    print("-" * WIDTH)

    rows = [
        ("Fast decision", "Detailed reasoning"),
        ("Bounded choices", "Open-ended generation"),
        ("Few output tokens", "Many output tokens"),
        ("Structured output", "Natural language"),
        ("Classification", "Explanation"),
        ("Routing", "Planning"),
        ("Detection", "Problem solving"),
    ]

    for left, right in rows:
        print(f"{left:<38} {right:<38}")

    print()

    paragraph(
        "These are not strict categories. A modern LLM can perform "
        "both kinds of work. The distinction is about how we use "
        "the model and what output we require."
    )

    pause()


# ============================================================
# HOW OPENJEV WORKS
# ============================================================

def how_openjev_works():

    clear()

    title("7. HOW DOES OPENJEV WORK?")

    print()

    show_box([
        "USER MESSAGE",
        "      ↓",
        "LOCAL QWEN3 0.6B",
        "      ↓",
        "READ MODEL LOGITS",
        "      ↓",
        "MASK TO VALID ANSWERS",
        "      ↓",
        "SOFTMAX",
        "      ↓",
        "PROBABILITIES",
    ])

    print()

    paragraph(
        "The key idea is that OpenJev does not need to generate a "
        "long natural-language explanation and then parse that "
        "explanation back into a decision. It reads the model's "
        "probabilities for the permitted answer tokens."
    )

    print("For example:")
    print()
    print("  complaint   0.91")
    print("  request     0.07")
    print("  question    0.02")
    print()
    print("The application can directly use the selected decision.")

    pause()


# ============================================================
# THREE PRIMITIVES
# ============================================================

def primitives():

    clear()

    title("8. OPENJEV'S THREE DECISION TYPES")

    print()

    print("CHOICE")
    print("------")
    print("Choose one option.")
    print()
    print("  billing       2%")
    print("  technical    96%")
    print("  sales          2%")
    print()
    print("  → technical")

    print()
    print("NOUL")
    print("----")
    print("Yes / No decision.")
    print()
    print("  Yes           97%")
    print("  No             3%")

    print()
    print("SCORE")
    print("-----")
    print("Ordered levels.")
    print()
    print("  Negative      80%")
    print("  Neutral       18%")
    print("  Positive       2%")
    print()
    print("  → weighted score")

    pause()


# ============================================================
# NORMAL LLM VS OPENJEV
# ============================================================

def compare_demo():

    clear()

    title("9. OUR COMPARE DEMO")

    paragraph(
        "Our compare demo deliberately uses the SAME Qwen3 0.6B "
        "model through the SAME local Ollama server."
    )

    show_box([
        "SAME INPUT",
        "     │",
        "     ├───────────────┐",
        "     │               │",
        "     ▼               ▼",
        "NORMAL LLM       OPENJEV",
        "     │               │",
        "     ▼               ▼",
        "GENERATE TEXT    MAKE DECISION",
    ])

    print()

    print("Example input:")
    print()
    print(
        '  "The server has been down for two hours. '
        'Fix this immediately."'
    )

    print()
    print("Normal LLM might return:")
    print()
    print(
        '  "This appears to be an urgent technical issue. '
        'You should investigate the server..."'
    )

    print()
    print("OpenJev returns:")
    print()
    print("  intent")
    print("    complaint    91%")
    print("    request       8%")
    print("    question      1%")
    print()
    print("  urgent")
    print("    Yes           98%")
    print("    No             2%")

    pause()


# ============================================================
# WHY THIS MATTERS
# ============================================================

def why_it_matters():

    clear()

    title("10. WHY DOES THIS MATTER?")

    paragraph(
        "Suppose a company receives one million customer messages. "
        "Most messages do not require a long AI-generated answer. "
        "They may only need a small decision."
    )

    print("Examples:")
    print()

    bullet("Which department?")
    bullet("Is this urgent?")
    bullet("Is this spam?")
    bullet("Should this go to a human?")
    bullet("Which workflow?")
    bullet("How severe is the problem?")
    bullet("Which tool should run next?")

    print()

    paragraph(
        "For these tasks, generating a paragraph and then asking "
        "another piece of software to interpret that paragraph can "
        "be unnecessary. A typed decision interface can expose the "
        "decision directly."
    )

    pause()


# ============================================================
# WHAT OPENJEV IS NOT
# ============================================================

def limitations():

    clear()

    title("11. WHAT OPENJEV IS NOT")

    bullet("It is not a replacement for every LLM workload.")
    bullet("It is not a reasoning engine for arbitrary multi-step problems.")
    bullet("It does not magically make a small model intelligent.")
    bullet("Its probabilities are not automatically calibrated correctness guarantees.")
    bullet("Prompt wording can affect the resulting distribution.")
    bullet("Our Qwen3 0.6B experiment is a small-model experiment.")

    print()

    paragraph(
        "OpenJev's own documentation describes decision questions "
        "as being suited to bounded answers and notes limitations "
        "around prompt sensitivity, multilingual performance and "
        "multi-step reasoning."
    )

    pause()


# ============================================================
# OUR EXPERIMENT
# ============================================================

def experiment():

    clear()

    title("12. OUR LOCAL EXPERIMENT")

    print()

    print("Hardware / software path")
    print()
    print("  Mac")
    print("   ↓")
    print("  Ollama")
    print("   ↓")
    print("  Qwen3 0.6B")
    print("   ↓")
    print("  ┌─────────────────────────────┐")
    print("  │                             │")
    print("  ▼                             ▼")
    print("Normal LLM                  OpenJev")
    print("generation                  decision")
    print("  │                             │")
    print("  ▼                             ▼")
    print("Text                        Choice")
    print("                            Noul")
    print("                            Score")

    print()

    print("We can measure:")
    print()
    bullet("Accuracy")
    bullet("Latency")
    bullet("Confidence")
    bullet("Probability distributions")
    bullet("Ambiguous cases")
    bullet("German messages")
    bullet("Boundary cases")

    pause()


# ============================================================
# FINAL
# ============================================================

def final():

    clear()

    title("13. THE BIG IDEA")

    show_box([
        "NORMAL LLM",
        "Think / generate / explain",
        "",
        "OPENJEV",
        "Decide / classify / route",
    ])

    print()

    paragraph(
        "The interesting idea is not that OpenJev replaces the LLM. "
        "It is that a local LLM can be used as a fast decision "
        "component inside a larger system."
    )

    print()

    print("A practical architecture can therefore look like:")
    print()

    print("  User")
    print("    ↓")
    print("  OpenJev")
    print("    ↓")
    print("  Is this complex?")
    print("    │")
    print("    ├── NO  → automated workflow")
    print("    │")
    print("    └── YES → normal LLM / agent")
    print()

    print("=" * WIDTH)
    print("END OF DEMO")
    print("=" * WIDTH)
    print()


# ============================================================
# MAIN
# ============================================================

def main():

    intro()
    what_is_jev()
    what_is_openjev()
    what_jev_means()
    system_one()
    system_two()
    comparison()
    how_openjev_works()
    primitives()
    compare_demo()
    why_it_matters()
    limitations()
    experiment()
    final()


if __name__ == "__main__":
    main()
