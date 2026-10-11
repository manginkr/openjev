#!/bin/bash
set -u

MODEL="${OPENJEV_MODEL:-qwen3:0.6b}"
BACKEND="${OPENJEV_BACKEND:-ollama}"

run_case() {
  local id="$1"
  local category="$2"
  local text="$3"

  echo
  echo "============================================================"
  echo "$id | $category"
  echo "$text"
  echo "------------------------------------------------------------"

  openjev-easy --backend "$BACKEND" --model "$MODEL" --once "$text"
}

run_case "U01" "urgent" "The production server is completely down and customers cannot access the service."
run_case "U02" "urgent" "A fire alarm is active and people may still be inside the building."
run_case "U03" "urgent" "The main database is corrupted and today's customer orders cannot be processed."
run_case "U04" "urgent" "A critical security vulnerability is being actively exploited on our public server."

run_case "N01" "non-urgent" "I would like to change the color of my profile next week."
run_case "N02" "non-urgent" "The monthly report has a minor formatting issue, but all numbers are correct."
run_case "N03" "non-urgent" "I might reorganize the office files sometime next month."
run_case "N04" "non-urgent" "The website logo looks slightly blurry on one page, but everything works."

run_case "A01" "ambiguous" "The website is slower than usual, but customers can still complete purchases."
run_case "A02" "ambiguous" "My laptop battery now lasts about two hours instead of four."
run_case "A03" "ambiguous" "One customer says the application feels unreliable, but we have no outage reports."
run_case "A04" "ambiguous" "The payment page failed once, then worked normally on the next attempt."

run_case "F01" "financial" "We were charged the same $5,000 supplier invoice twice."
run_case "F02" "financial" "A payment processor has stopped sending us settlement funds and revenue is affected."
run_case "F03" "financial" "A customer says they were charged twice for the same order."
run_case "F04" "financial" "Our finance spreadsheet contains a small rounding difference of two cents."

run_case "S01" "security" "Someone accessed an employee account without authorization."
run_case "S02" "security" "We received a suspicious login alert, but the employee confirms it was them."

run_case "C01" "customer complaint" "The customer says they have been waiting three days for a refund and are extremely frustrated."
run_case "C02" "customer complaint" "The customer dislikes the new dashboard layout but can still use the product normally."

