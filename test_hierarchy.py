#!/usr/bin/env python3

from openjev.easy import make_engine
from openjev.types import Noul, Choice, Score


MODEL = "qwen3:0.6b"


def ask(engine, state, question_id, question):
    result = engine.system_one(
        state,
        {question_id: question},
    )
    return result["answers"][question_id]


def show(title, answer):
    print(f"\n{title}")
    print("-" * len(title))
    print(answer)


def run_case(name, state):
    print("\n" + "=" * 70)
    print(name)
    print("=" * 70)
    print("STATE:")
    print(state)

    engine = make_engine(
        backend="ollama",
        model=MODEL,
    )

    # ------------------------------------------------------------
    # LEVEL 1: URGENCY
    # ------------------------------------------------------------

    urgent = ask(
        engine,
        state,
        "urgent",
        Noul(
            instructions="Is this situation urgent and requiring prompt attention?"
        ),
    )

    show("LEVEL 1 — URGENCY", urgent)

    # OpenJev's noul answer is the probability of Yes.
    urgent_probability = urgent.get("noul", 0.0)

    if urgent_probability >= 0.70:

        # --------------------------------------------------------
        # LEVEL 2A: URGENT → CATEGORY
        # --------------------------------------------------------

        category = ask(
            engine,
            state,
            "category",
            Choice(
                instructions="What is the primary category of this incident?",
                criteria={
                    "technical": "Service outage, infrastructure, software failure",
                    "security": "Unauthorized access, attack, vulnerability",
                    "financial": "Payments, money loss, billing, financial exposure",
                    "customer": "Customer complaint or customer experience problem",
                },
            ),
        )

        show("LEVEL 2 — URGENT CATEGORY", category)

        selected_category = category.get("choice")

        # --------------------------------------------------------
        # LEVEL 3: CATEGORY-SPECIFIC DECISION
        # --------------------------------------------------------

        if selected_category == "security":
            followup = ask(
                engine,
                state,
                "active_security",
                Noul(
                    instructions="Is there evidence that a security incident is currently active?"
                ),
            )

            show("LEVEL 3 — ACTIVE SECURITY INCIDENT", followup)

        elif selected_category == "technical":
            followup = ask(
                engine,
                state,
                "customer_impact",
                Noul(
                    instructions="Are customers currently unable to use an important part of the service?"
                ),
            )

            show("LEVEL 3 — CUSTOMER IMPACT", followup)

        elif selected_category == "financial":
            followup = ask(
                engine,
                state,
                "financial_exposure",
                Score(
                    instructions="How serious is the financial exposure?",
                    criteria=[
                        "minimal",
                        "moderate",
                        "significant",
                        "critical",
                    ],
                ),
            )

            show("LEVEL 3 — FINANCIAL EXPOSURE", followup)

        elif selected_category == "customer":
            followup = ask(
                engine,
                state,
                "customer_severity",
                Score(
                    instructions="How severe is the customer impact?",
                    criteria=[
                        "minor",
                        "moderate",
                        "serious",
                        "critical",
                    ],
                ),
            )

            show("LEVEL 3 — CUSTOMER SEVERITY", followup)

    else:

        # --------------------------------------------------------
        # LEVEL 2B: NON-URGENT → IMPACT
        # --------------------------------------------------------

        impact = ask(
            engine,
            state,
            "impact",
            Score(
                instructions="How significant is the current impact?",
                criteria=[
                    "minimal",
                    "minor",
                    "moderate",
                    "significant",
                ],
            ),
        )

        show("LEVEL 2 — NON-URGENT IMPACT", impact)

    print("\nFINAL DECISION PATH COMPLETE")


if __name__ == "__main__":

    cases = [
        (
            "CASE 1 — TECHNICAL OUTAGE",
            """
            The production server is completely down.
            Customers cannot log in and orders are failing.
            We are losing approximately €500 per hour.
            """,
        ),
        (
            "CASE 2 — SECURITY",
            """
            An employee account was accessed from an unknown country.
            The employee says they did not make the login.
            Several unusual API requests were made afterward.
            """,
        ),
        (
            "CASE 3 — FINANCIAL",
            """
            Our payment processor has stopped sending settlement funds.
            We have not received today's €80,000 settlement.
            Customers can still use the service.
            """,
        ),
        (
            "CASE 4 — CUSTOMER",
            """
            A customer has been waiting three days for a refund.
            They are extremely frustrated and have contacted support twice.
            The product itself is working normally.
            """,
        ),
        (
            "CASE 5 — NON-URGENT",
            """
            The website logo is slightly blurry on one page.
            All functionality works normally and customers can complete purchases.
            """,
        ),
    ]

    for name, state in cases:
        run_case(name, state)
