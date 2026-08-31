"""
Support Ticket Automation — main entry point.

Run this file after setup:

    python app.py

Flow:
    load tickets → build workflow → process each ticket → save results
"""

import json
import sys
from pathlib import Path

from src.llm import create_llm
from src.workflow import build_workflow, process_ticket

PROJECT_ROOT = Path(__file__).resolve().parent
INPUT_FILE = PROJECT_ROOT / "data" / "support_tickets.json"
OUTPUT_FILE = PROJECT_ROOT / "data" / "output" / "support_ticket_results.json"


def load_file(file_path):
    """
    Load support tickets from a JSON file.

    Args:
        file_path (str | Path): Path to the JSON input file.

    Returns:
        list: A list of support ticket dictionaries.

    Example:
        tickets = load_tickets("data/support_tickets.json")
        print(len(tickets))
    """
    path = Path(file_path)
    if not path.exists():
        print(f"Error: Input file not found in the path: {path}")
        sys.exit(1)

    try:
        with path.open("r" , encoding="utf-8") as file:
            tickets = json.load(file)
    except json.JSONDecodeError as error:
        print(f"Error: Invalid JSON in {path}: {error}")
        sys.exit(1)

    if not isinstance(tickets , list) or not tickets:
        print("Error: support_tickets.json must contain non-empty list of tickets")
        sys.exit(1)

    return tickets

def save_results(results, file_path):
    """
    Save processed ticket results to a JSON file.

    Creates the output directory automatically if it does not exist.

    Args:
        results (list): List of TicketResult objects or dictionaries.
        file_path (str | Path): Destination JSON path.

    Returns:
        Path: The path where results were written.

    Example:
        save_results(results, "data/output/support_ticket_results.json")
    """
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    # Convert Pydantic models into plain dictionaries for JSON saving.
    serializable = [
        result.model_dump() if hasattr(result, "model_dump") else result
        for result in results
    ]

    with path.open("w", encoding="utf-8") as file:
        json.dump(serializable, file, indent=2, ensure_ascii=False)

    return path


def main():
    """
    Orchestrate the full support ticket automation run.

    Returns:
        None
    """
    print("=" * 40)
    print("AI SUPPORT TICKET AUTOMATION")
    print("=" * 40)
    print()

    # 1. Load tickets
    tickets = load_file(INPUT_FILE)
    print(f"Loaded {len(tickets)} tickets from {INPUT_FILE.name}")

    # 2. Initialize LLM and build workflow once
    llm = create_llm()
    workflow = build_workflow(llm)

    results = []

    # 3. process each ticket one by one
    for ticket in tickets:
        ticket_id = ticket.get("ticket_id" , "UNKNOWN")
        print(f"Processing Ticket {ticket_id}...")

        try:
            result = process_ticket(ticket , workflow)
            results.append(result)
        except Exception as error:
            # Keep going so one bad ticket does not stop the whole demo.
            print(f"ERROR while processing {ticket_id}: {error}")
            print()
            continue

        print()

    # 4. Save whatever succeeded
    if not results:
        print("No tickets were processed successfully.")
        sys.exit(1)

    output_path = save_results(results, OUTPUT_FILE)

    print("=" * 40)
    print("Processing complete!")
    print("Results saved to:")
    print(output_path.as_posix())
    print("=" * 40)


if __name__ == "__main__":
    main()

