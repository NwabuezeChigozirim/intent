# Playbook: working with intent and governance

How to use the two plugins together, day to day. Written for the owner, not the agent.

## The picture

Three things have to be true before you can stop watching an agent work:

| Layer | Question | Plugin | Enforced by |
|---|---|---|---|
| Intent | Does the agent know what I want? | `intent` | Conversation, a spec, tickets |
| Codebase | Is bad code hard to write? | `governance` | Rules, linters, hooks, CI |
| Verification | Did the agent prove it works? | `governance` | Stages, checks, receipts |

`intent` ends where a ticket is ready. `governance` starts there. They meet at one point:

> A ticket's acceptance criteria become the frozen checks of a governance stage.

So a criterion has to be something a command or a driven run of the app can prove true or false. "Archiving three selected notes moves all three to the archive" is a criterion. "Works well" is not.

## Words used here

| Word | Meaning |
|---|---|
| Skill | A set of instructions the agent reads. Some you start by typing `/name`; others the agent loads itself when the task fits. |
| Grilling | The agent interviews you until nothing is assumed. |
| Glossary | `GLOSSARY.md`: the project's agreed words, so you and the agent mean the same thing. |
| ADR | A short record of one hard-to-reverse decision, under `docs/adr/`. |
| Spec | One GitHub issue describing the problem, the solution, user stories and decisions. |
| Ticket | One GitHub issue for one thin, complete, demonstrable piece of the spec. |
| Blocking link | "This ticket cannot start until that one is done." |
| Frontier | The tickets (or questions) that can start right now. |
| Stage | One ticket being built under governance, from contract to receipt. |
| Contract | The stage's written intent, acceptance list and check commands. |
| Freeze | Your one approval per stage. You run the command; the agent cannot. |
| Receipt | The record that every check passed on the exact final code. |
| Rule | An enforced check on the code (a banned pattern, a file length limit, a linter). |
| Baseline | The old violations a rule tolerates. They may shrink, never grow. |
| Gate | The CI job that fails a pull request with no matching receipt. |

## One-time setup

### On each machine

1. Install `gh` and sign in:

```bash
gh auth login
```

2. From a checkout of `governance`:

```bash
python scripts/install.py
```

3. From a checkout of `intent`:

```bash
python scripts/install.py
```

4. Restart Cursor, then run `/setup-pstack` once to pick models.

### In each project

1. Adopt governance (rules, strict linters, CI gate):

```bash
python <governance checkout>/scripts/adopt.py --repo .
```

If it prints `NOT DONE`, install the tools it names, then run `python tools/governance/rulekit baseline`.

2. Commit the result to the main branch and make the `gate` job a required check on GitHub.
3. In Cursor, run `/setup-intent` and accept the defaults (GitHub issues, five triage labels, one glossary). It will hand you a short `## Agent skills` block to paste into `AGENTS.md` yourself, because the hook does not let the agent edit that file outside a stage.
4. If the project has an app to drive, run `/create-verification-skill` so agents can prove behavior in the real app.

## The main flow: idea to merged code

| Step | You type | What happens | What you do |
|---|---|---|---|
| 1 | `/grill-with-docs <idea>` | Rounds of questions, each with a recommended answer. Glossary updated as terms settle. | Answer. "Yes" accepts the recommendation. |
| 2 | `/to-spec` | Spec written from the conversation and published as an issue. | Confirm the test seams it proposes. |
| 3 | `/to-tickets` | Spec split into tickets with blocking links. | Approve or adjust the breakdown. |
| 4 | `/implement <ticket>` in a new chat | Agent drafts the stage contract from the ticket. | Read the contract. Run the freeze command it gives you. |
| 5 | (nothing) | Agent builds, runs the checks, gets an independent verdict, closes the stage, opens the pull request. | Nothing, unless it stops and says why. |
| 6 | Merge | The CI gate confirms a receipt matches the code. | Merge, or let it merge when you trust it. |
| 7 | `/correct` when you had to correct the agent | The correction becomes an enforced rule. | Approve the rule. |

Keep steps 1 to 3 in one chat. Start a new chat for each ticket in step 4.

For a whole spec at once, replace step 4 with `/implement-spec <spec issue>`. It runs the tickets in parallel and gives you the freeze commands in batches.

## When I want to..., I type...

### Decide what to build (intent)

| I want to | Type |
|---|---|
| Be interviewed about a feature | `/grill-with-docs i want <feature>` |
| Be interviewed about something with no repo | `/grill-me <plan>` |
| Check a request against the real need behind it | `/need-first review this` |
| Settle a confusing word, or record a big decision | `/domain-modeling <the word or decision>` |
| Get a fact researched from primary sources | `/research <question>` |
| See an idea working before committing to it | `/prototype <question>` |
| Decide if I need a queue, cache or events | `/systems-design <capability and its load>` |
| Plan a project too big or unclear for one chat | `/wayfinder <idea>`, then `/wayfinder <map issue>` each session |
| Ask someone else for the answers | `/to-questionnaire <who and what>` |

### Write it down (intent)

| I want to | Type |
|---|---|
| Turn the conversation into a spec | `/to-spec` |
| Split the spec into tickets | `/to-tickets` |
| Sort incoming bug reports and requests | `/triage` |

### Build and prove (governance)

| I want to | Type |
|---|---|
| Build one ticket | `/implement <ticket>` |
| Build a whole spec in parallel | `/implement-spec <spec issue>` |
| Do a task that has no ticket | `/govern <goal, and how to tell it's done>` |
| Fix a bug | `/govern <symptom>. repro first, then fix and verify.` |
| Have other models try to break a change | `/interrogate` |
| Hunt for bugs nobody reported | `/govern fuzz <area>` |
| Get a pull request green | `/govern babysit this pr` |
| Understand how code works, or why | `/how <thing>`, `/why <thing>` |
| Have a change explained plainly | `/teach` |

### Keep the code good (governance)

| I want to | Type |
|---|---|
| Stop a mistake from happening again | `/correct` |
| Add one enforced rule | `/rulekit <what to ban or limit>` |
| Find bad habits that are spreading | `/garden` |
| Remove old violations a rule still tolerates | `/govern clean up the baseline for <rule ID>` |
| Find modules worth restructuring | `/improve-codebase-architecture` (intent) |

### When I'm lost

| I want to | Type |
|---|---|
| Know which planning skill fits | `/intent-help <question>` |
| Know which building or checking skill fits | `/govern-help <question>` |
| Hear the last message in plain words | `/wait-what` or `/bro` |
| Catch up on this chat | `/ketchup` |
| Move the work to another chat or person | `/handoff` |

## What the agent does without being asked

You do not type these. The agent loads them when the task fits:

- From intent: `grilling`, `domain-modeling`, `need-first`, `systems-design`, `codebase-design`, `research`, `prototype`, `wizard`, `writing-for-agents`.
- From governance: the `principle-*` skills, `architect`, `tdd`, `unslop`, `no-comments`, `technical-writing` and the verification skills, as `/govern`'s steps call for them.

And these run with no agent involved at all:

- The guard hook blocks edits when no stage is frozen, and blocks changes to rules, linter configs and the baseline.
- The CI gate fails a pull request that has no matching receipt.

## What needs me, and what doesn't

| Needs you | Does not need you |
|---|---|
| Answering the interview | Looking up facts in the code or docs |
| Approving the ticket breakdown | Writing the spec and tickets |
| Freezing each stage contract | Building, testing, reviewing |
| Approving a new rule | Enforcing existing rules |
| Merging (until you choose otherwise) | Closing the stage and writing the receipt |

Your two real decisions per ticket are the interview answers and the freeze. Everything else is checkable after the fact.

## A worked example

You want users to archive several notes at once.

1. `/grill-with-docs i want bulk archive in the notes list`
   The agent asks who archives in bulk and why, whether archive can be undone, what happens to notes shared with others, what the limit is. It adds "Archive" to the glossary.
2. `/to-spec` publishes the spec as an issue.
3. `/to-tickets` proposes three tickets:
   - Archive several selected notes from the list (no blockers)
   - Undo a bulk archive (blocked by the first)
   - Shared notes are skipped with a message (blocked by the first)

   Each has criteria such as "selecting three notes and choosing Archive moves all three to the archive".
4. New chat: `/implement 41`. The agent shows the contract: the intent, the criterion, and two checks (a test command, a driven run of the app). You run the freeze command.
5. The agent builds, proves, closes, and opens the pull request with the receipt.
6. You notice it left a `// TODO: handle errors` comment. You say so, then `/correct`. A rule now blocks that pattern for every future agent.

## When something goes wrong

| What you see | What to do |
|---|---|
| The agent asks one question at a time | "Ask the whole frontier in one round." |
| The agent starts coding during the interview | "Do not act until I confirm we have a shared understanding." |
| A ticket covers only one layer | Reject it in `/to-tickets`. Each ticket must be showable working on its own. |
| `/implement` stops on a criterion it cannot check | Rewrite the criterion on the ticket as something provable. |
| "This project requires a stage before files change" | Working as designed. The agent writes the contract; you freeze it. |
| The agent asks you to run a command with `--owner-approved` | Working as designed. Read the contract, then run it. |
| The CI `gate` job fails | Something changed after the stage closed. Rerun checks, close again, commit the new receipt. |
| The hook blocks the agent from writing `GLOSSARY.md`, `docs/adr/` or `docs/agents/` | The project was adopted before governance exempted planning documents. Add `GLOSSARY.md`, `**/GLOSSARY.md`, `docs/adr/**`, `**/docs/adr/**`, `docs/agents/**` and `.scratch/**` to `exempt` in `.governance/config.json`. |
| "The tracker was not provided" | Run `/setup-intent`. |
| `gh` commands fail | Run `gh auth login`. |

## Known limits

- Neither plugin has been run end to end in Cursor yet. The tests cover the scripts, hooks and package structure, not agent behavior.
- A file written by a shell command bypasses the edit-time hook. The CI gate still catches it.
- Receipts can be forged by someone determined; the gate is a safeguard against mistakes, not against an adversary.
- `/implement-spec` batching the freeze commands across parallel tickets is untested.
- `wizard` needs bash: Linux, macOS, or Git Bash on Windows.

## Running them in any order

| Order | Works | Notes |
|---|---|---|
| intent, then governance | Yes | The main flow. |
| governance alone | Yes | `/govern <task>` needs no spec or ticket. |
| governance, then intent | Yes | A finding from `/garden` or `/improve-codebase-architecture` becomes an idea for `/grill-with-docs`. |
| intent alone | Planning only | `/implement` stops when governance is not installed. |
