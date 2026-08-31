# AI Support Ticket Automation

A beginner-friendly LangChain project that processes customer support tickets through a clear multi-stage workflow.

This is an **educational** application for learning LangChain fundamentals — not a production support system.

---

## 1. Project Overview

The app reads support tickets from a JSON file and runs each ticket through:

1. **Triage** — classify category, priority, and language
2. **Routing** — send the ticket to a specialized analysis chain
3. **Case Analysis** — extract category-specific details
4. **Resolution** — decide what should happen next
5. **Response** — write a customer-facing reply
6. **Final Output** — save a structured JSON result

---

## 2. Workflow

```text
Support Ticket
      │
      ▼
1. Ticket Triage
      │
      ▼
2. Routing (RunnableBranch)
      │
      ├── Billing Chain
      ├── Technical Chain
      ├── Account Chain
      ├── Cancellation/Refund Chain
      ├── Order/Delivery Chain
      └── General Chain
      │
      ▼
3. Case Analysis
      │
      ▼
4. Resolution Decision
      │
      ▼
5. Response Generation
      │
      ▼
6. Final Structured Output
```

Each stage has one job. For example, the response generator does **not** invent a new business decision — it follows the resolution from Stage 4.

---

## 3. LangChain Concepts Demonstrated

| Concept           | Where Used                                      |
| ----------------- | ----------------------------------------------- |
| LLM               | All LLM chains via `ChatGroq`                 |
| Prompt Templates  | Prompt files loaded into `ChatPromptTemplate`   |
| Structured Output | Triage, case analysis, and resolution schemas   |
| Routing           | Category-based selection with `RunnableBranch`  |
| Chains            | Individual processing stages (`prompt \| llm`)  |
| Runnables         | Workflow composition and routing                |
| Pydantic          | Structured schemas in `src/schemas.py`          |

---

## 4. Project Structure

```text
support-ticket-automation/
├── .env.example          # Example environment variables
├── .gitignore
├── README.md
├── requirements.txt
├── app.py                # Main entry point
├── data/
│   ├── support_tickets.json
│   └── output/           # Generated results go here
├── prompts/
│   ├── classification_prompt.txt
│   ├── case_analysis_prompt.txt
│   ├── resolution_prompt.txt
│   └── response_prompt.txt
└── src/
    ├── llm.py            # Create the GROQ AI chat model
    ├── schemas.py        # Pydantic models
    ├── chains.py         # Triage, routing, analysis, resolution, response
    └── workflow.py       # Connects the stages together
```

---

## 5. Setup

```bash
git clone <your-repo-url>
cd support-ticket-automation
python -m venv venv
```

Activate the virtual environment:

**Windows (PowerShell):**

```powershell
.\venv\Scripts\Activate.ps1
```

**macOS / Linux:**

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create your environment file:

1. Copy `.env.example` to `.env`
2. Add your OpenAI API key:

```text
GROQ_API_KEY=your_real_api_key_here
GROQ_MODEL=groq_model
```

---

## 6. Run

From the project root:

```bash
python app.py
```

The app will:

- load tickets from `data/support_tickets.json`
- process each ticket through the workflow
- print progress in the terminal
- save results to `data/output/support_ticket_results.json`

---

## 7. Example Output

Terminal:

```text
========================================
AI SUPPORT TICKET AUTOMATION
========================================

Processing ticket: TKT-1001
Category: billing
Priority: high
Routing to: Billing Chain
Resolution: escalate
Human Required: Yes

Processing ticket: TKT-1002
Category: technical
Priority: medium
Routing to: Technical Chain
Resolution: self_service
Human Required: No

========================================
Processing complete!
Results saved to:
data/output/support_ticket_results.json
========================================
```

Example JSON result (simplified):

```json
{
  "ticket_id": "TKT-1001",
  "customer_name": "Rahul Sharma",
  "category": "billing",
  "priority": "high",
  "language": "English",
  "resolution_type": "escalate",
  "recommended_action": "Send the case to billing for duplicate-charge verification.",
  "requires_human": true,
  "response": "Hi Rahul, thanks for reaching out..."
}
```

---

## 8. How to Explore the Code (for students)

A good learning path:

1. Read `data/support_tickets.json` — the input
2. Read `src/schemas.py` — what structured data looks like
3. Read the prompt files in `prompts/` — what we ask the LLM
4. Read `src/chains.py` — how prompts + LLMs become chains
5. Read `src/workflow.py` — how stages connect
6. Run `app.py` and inspect `data/output/support_ticket_results.json`

Suggested experiments:

- Change a prompt and re-run
- Add a new sample ticket
- Adjust allowed priorities or resolution types in `schemas.py`

---

## 9. Future Improvements

Ideas for later versions (not included in v1):

- RAG over a help-center knowledge base
- Tool calling for order lookup or refund status
- Database storage for tickets and results
- Streamlit UI for demos
- Human-in-the-loop review before sending replies
- Ticket history / conversation context
- Evaluation and quality scoring
- Monitoring and logging dashboards

---

## License

Educational project — use and modify freely for learning and tutorials.
