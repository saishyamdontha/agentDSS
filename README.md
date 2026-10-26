# AgentDSS

A human-in-the-loop decision pipeline for supply chain disruptions. Four LLM agents
(supplier, inventory, logistics, finance) each propose ranked options with a confidence
score. At every step a person accepts an option or overrides it, and that decision is
passed on as context to every later agent.

The project asks one question: **when does a human override actually improve the decision,
and when should the agent's option simply be taken?**

## Why I built this

The Decision Support Systems course at BTH is where I learned how to structure a decision:
options, criteria, consequences, and who makes the final call. The PEMA port operations
challenge, where our team reached the final, showed me how much of real operations still
depends on people coordinating decisions by hand. AgentDSS is my attempt to bring the two
together: AI agents that give decision-makers better options, while the person stays
responsible for the decision.

## How it works

1. An operator describes a disruption (supplier delay, demand spike, route failure, or a
   combination).
2. The supplier agent reads its data and returns 2-3 ranked options with confidence scores.
3. Before the person commits, an **impact preview** scores each option on cost, lead-time
   and risk changes:
   `Impact(d) = w_c * dCost + w_t * dLeadTime + w_r * dRisk`
   The preview is deterministic code, not an LLM call, so it adds no run-to-run variance.
4. The person accepts an option or writes an override.
5. The **context manager** stores the decision as a structured record and passes the full
   decision history to the next agent.
6. Steps 2-5 repeat for inventory, logistics and finance, producing a complete decision log.

Design rule: **code computes the numbers, the LLM explains them.** Agents do not invent
costs or scores.

## Decision record

Every step is stored as a structured record, not free text, so override behaviour can be
queried and scored:

| Field | Meaning |
|---|---|
| `event_id`, `timestamp` | identity and time |
| `agent_role` | supplier, inventory, logistics or finance |
| `options_presented` | the ranked options with confidence scores |
| `decision_type` | accepted option or override |
| `decision_text` | what was decided |
| `override_flag` | whether the person overrode the agent |
| `preview_shown` | the impact preview the person saw |

## Evaluation

The evaluation is designed before the full system, not added at the end.

- **Hidden-knowledge scenarios:** each synthetic scenario contains a fact the agents cannot
  see but the human operator knows (for example, that a supplier has an unreported
  problem). This makes it possible to test whether overrides add real information.
- **Two conditions per scenario:** the agent's top option accepted automatically, against a
  run with human overrides.
- **Primary metric:** constraint-violation rate, checked by code, not by an LLM.
- **Reproducibility:** fixed scenario seed, fixed model settings, versioned prompts, raw
  outputs stored, and negative results reported.

## Status

| Part | Status |
|---|---|
| Context manager and decision record, 9 unit tests | Done |
| Database persistence (SQLAlchemy) | Done |
| Seeded scenario generator | Done (being moved to hidden-knowledge scenarios) |
| Impact preview | Done |
| Supplier agent, on real shipment data | Done |
| End-to-end slice: supplier agent -> preview -> human decision -> context | Working |
| Inventory, logistics and finance agents | In progress |
| Evaluation harness and results | Planned |

## Data

Backbone dataset: *Global Supply Chain Risk and Logistics 2024-2026* (Kaggle), 5,000
shipment records. Each agent is designed to read its own data source, which raises the
data interoperability problem the context manager is built to handle.

## Stack

Python, local LLMs via Ollama, SQLAlchemy, PostgreSQL, pandas, NumPy, pytest

## Run the tests

    pip install -r requirements.txt
    pytest test_context_manager.py

## Proposal

The design and evaluation plan are in [`docs/`](docs/).

## History

Started in July 2026 as a three-person team project; developed solo since.
