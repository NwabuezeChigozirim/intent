# intent

A Cursor plugin that gets the agent to understand what you want before it builds.
It interviews you, keeps a shared vocabulary, writes one spec, and splits it into
tickets on GitHub. Building and proving each ticket is handed to the
[`governance`](https://github.com/NwabuezeChigozirim/governance) plugin.

Most of the skills are taken from Matt Pocock's
[skills](https://github.com/mattpocock/skills) (MIT), lightly adapted. Two come
from the earlier `agent-skills` suite: `need-first` and `systems-design`.

## How it fits with governance

| Layer | Question | Plugin |
|---|---|---|
| Intent | Does the agent know what you want? | `intent` |
| Codebase | Is bad code hard to write? | `governance` |
| Verification | Did the agent prove it works? | `governance` |

The join is one rule: a ticket's acceptance criteria become the frozen checks of a
`/govern` stage. `/to-tickets` therefore only accepts criteria a command or a driven
run of the app can prove true or false.

## The main flow

1. `/grill-with-docs`: the agent asks every open question, each with a recommended
   answer, until nothing is assumed. It updates `GLOSSARY.md` and writes a decision
   record when a choice is hard to reverse. It applies `need-first`, so a request is
   tested against the job behind it.
2. `/to-spec`: turns the conversation into one spec, published as a GitHub issue.
3. `/to-tickets`: splits the spec into vertical slices, each small enough for one
   fresh agent session, with blocking links between them.
4. `/implement <ticket>`: runs the ticket as one `/govern` stage. Or
   `/implement-spec` to run the whole ticket graph with parallel subagents.

For work too big or too unclear for one session, start with `/wayfinder` instead of
step 1. If you forget which skill fits, ask `/intent-help`.

[docs/PLAYBOOK.md](docs/PLAYBOOK.md) is the day-to-day guide to using this plugin and
`governance` together: setup, the flow, and which command to type for which goal.

## Skills

| Skill | You type it | What it does |
|---|---|---|
| `grill-with-docs` | yes | Interview plus glossary and decision records |
| `grill-me` | yes | The same interview with nothing saved, for work outside a repo |
| `to-spec` | yes | Conversation to spec |
| `to-tickets` | yes | Spec to vertical-slice tickets with blocking links |
| `implement` | yes | One ticket, built as a `/govern` stage |
| `implement-spec` | yes | A whole spec, tickets worked in parallel |
| `wayfinder` | yes | A map of decision tickets for large, unclear efforts |
| `triage` | yes | Sort incoming issues into agent-ready work |
| `improve-codebase-architecture` | yes | Survey the code for modules worth deepening |
| `handoff` | yes | Write a handoff file for another session |
| `to-questionnaire` | yes | Write questions for someone else to answer |
| `wait-what` | yes | Re-explain the last message in plain words |
| `setup-intent` | yes | Once per project: tracker, labels, doc layout |
| `intent-help` | yes | Answers questions about the plugin and hands you a prompt to send |
| `grilling` | agent | The interview itself |
| `domain-modeling` | agent | Glossary and decision records |
| `need-first` | agent | Request versus the job behind it |
| `systems-design` | agent | Is a queue, cache or event system justified |
| `codebase-design` | agent | Vocabulary for deep modules |
| `research` | agent | Background research into a cited file |
| `prototype` | agent | Throwaway code that answers one design question |
| `wizard` | agent | A step-by-step bash script for setup only a human can do (needs bash: Linux, macOS or Git Bash) |
| `writing-for-agents` | agent | How to write skills and agent docs |

## Changes from the upstream skills

- `implement` and `implement-spec` build through `/govern` instead of upstream's
  `tdd` and `code-review` skills.
- `grill-with-docs`, `to-spec` and `to-tickets` apply `need-first`.
- `to-tickets` requires provable acceptance criteria.
- The setup skill is `setup-intent`, the router is `intent-help`, and GitLab support
  is removed.
- "Call the Skill tool" is reworded to "load and follow the skill", since Cursor
  has no Skill tool.
- Not included: `tdd`, `code-review`, `retro`, `diagnosing-bugs`, `pr` and `teach`
  (governance covers them).

## Install

Install `governance` first. Then:

```bash
python scripts/install.py
```

Restart Cursor. In each project, run `/setup-intent` once and choose GitHub issues.
The GitHub tracker uses the `gh` command, which must be installed and signed in.

## Verify

```bash
python -B -m unittest discover -s tests -v
```

The tests check the package structure: every skill has matching frontmatter, every
skill a document names ships with the plugin or is a known governance skill, relative
links resolve, and the installer works. They do not test how an agent behaves when it
follows the skills.

## Licence

MIT. Upstream licence text is in `THIRD_PARTY_LICENSE-mattpocock-skills`.
