# Agent evaluation primitives

A small vocabulary for building an AI agent that stays testable.

The agent is an executor. The developer (or a product owner) owns the contract: input shape, output shape, rules, and tools. These five words describe how that contract is enforced.

| Word | When it runs | What it returns | Who owns it |
|---|---|---|---|
| Task | Defines work | A spec, not a value | Developer / PM |
| Runner | Online, per request | An output (or an error) | Engineer |
| Gate | Online, per request | `true` / `false` | Engineer writes the engine; PM owns the rules |
| Scorer | Offline, in batch | A number | Engineer |
| Judge | Offline, in batch | A number from an LLM | Engineer wires it; PM writes the rubric |

---

## Task

The unit of work.

A task is a prompt plus the expected output shape, plus the tools the agent may use.

```
Task
  input:   { ticket_id, customer_email }
  output:  { category, priority, draft_reply }
  tools:   [lookup_order, get_customer_history]
  rule:    priority = high only if order value > 500
```

The task does not run anything. It is the contract the runner must satisfy.

---

## Runner

The code that executes a task.

It calls the model, parses the result, hands it to the gate, and either returns or retries.

```
receive prompt
    → reason (model)
        → act (tool)
            → parse output
                → gate?
                    yes → stop, return output
                    no  → inject failure into prompt, retry (capped)
```

The runner is generic. It does not know the business rules. It only knows: call, parse, gate, retry, give up.

Typical shape:

```python
def run_agent(prompt, tools, rules, max_retries=3):
    for attempt in range(max_retries):
        raw = call_llm(prompt, tools)
        output = parse_json(raw)
        if gate(output, rules):
            log(output)          # keep for the offline path
            return output
        prompt = f"{prompt}\nPrevious attempt failed: {describe(output)}"
    raise AgentFailed(f"gave up after {max_retries} tries")
```

---

## Gate

The online check. A bouncer, not a critic.

The gate compares the output against a fixed rule list and returns a boolean. No score. No ranking. No second model call.

```
pass  → the pipeline stops, output is accepted
fail  → the runner retries, or raises if the cap is hit
```

Rules should not live in code. They live in a table or a YAML/JSON file that loads into memory at startup (and refreshes when edited).

```yaml
rules:
  - field: order_id
    type: required
  - field: priority
    type: enum
    values: [low, med, high]
  - field: draft_reply
    type: max_length
    value: 300
  - field: amount
    type: gt
    value: 0
```

The engine is one function: `gate(output, rules) -> bool`. Adding a rule is editing the file, not changing the runner.

Treat the rule file like a schema. New feature, new rule, same pull request. A stale gate is silent drift.

---

## Scorer

The offline function that turns an output into a number.

It runs later, on a sample of logged outputs — not on the live request. It can be:

- a regex or schema check with a numeric weight
- a similarity score against a gold answer
- a **judge** (see below)

The number is not fed back into the runner. It is a trend line for humans.

```
week 1   8.2
week 2   7.1
week 3   6.4    ← investigate
```

Use the same scorer to compare two prompt versions on a fixed set of examples before you ship.

---

## Judge

A scorer that uses an LLM.

```
"Rate this reply from 1 to 10 on helpfulness.
 Return only the number."
```

It is expensive (an extra model call per example) and opinionated (a rubric, not a checklist). That is why it stays offline and on a sample — one percent of traffic, or a fixed eval set of a hundred examples.

The judge does not decide whether a live reply ships. The gate does. The judge tells you whether quality is moving.

Log which rule-set version produced each scored batch. Otherwise the trend line lies when someone edits the gate.

---

## Online vs offline

```
ONLINE  (every request)
  task → runner → gate → user
                 ↘ log output + rule version

OFFLINE (schedule / sample)
  logged outputs → scorer / judge → score
                                 → human looks at the trend
                                 → maybe retune the prompt or add a rule
```

| | Online | Offline |
|---|---|---|
| Piece | Gate | Scorer / Judge |
| Cost | Cheap, no extra model | Extra model calls |
| Result | Boolean | Number |
| Purpose | Protect the user now | Protect quality over time |
| Failure | Retry or reject | Investigate, then change the contract |

The collected scores do not retrain the model by themselves. They tell a human when to change a prompt, a tool, or a rule — and then the eval set is run again to confirm the number moved the right way.

---

## How the pieces fit

```
Developer / PM
    writes the task
    writes the gate rules (config, not code)
    writes the judge rubric

Runner
    executes the task
    asks the gate: pass or fail?
    logs every output

Gate
    checklist against the loaded rules
    never scores

Judge / Scorer
    reads the log later
    writes a number
    never sits on the request path
```

The agent never sets the outcome. It inherits the task. The gate enforces the contract you already wrote. The judge measures whether that contract still produces good work.