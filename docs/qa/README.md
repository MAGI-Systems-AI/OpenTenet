# Tenet QA Test Suite

Five reproducible tests that show the measurable difference between a bare AI coding assistant and one running Tenet.

## Setup

Run each test **twice** — once in a bare AI session (no Tenet context loaded), once in a Tenet session. Use the **exact same prompt**. Record both outputs in the test file.

## Tests

| # | Test | What it catches |
|---|------|----------------|
| [1](test-1-verification.md) | The "Done" Lie | AI claiming completion without verification |
| [2](test-2-hallucination.md) | The Hallucination Trap | Invented APIs and file paths |
| [3](test-3-missed-ask.md) | The Missed Ask | Partial delivery on multi-part requests |
| [4](test-4-compounding.md) | The Compounding Test | Whether the system learns from mistakes |
| [5](test-5-premortem.md) | The Premortem Test | Whether the AI thinks before acting |

## Recording format

Each test file uses this structure:

```
## Prompt
[exact prompt — do not change between runs]
## No Tenet output
[paste transcript here]
## Tenet output
[paste transcript here]
## Difference
[one-line observation]
```

## The most important test

**Test 4 (Compounding)** is the hardest to fake and the most convincing to show others. It requires two sessions but produces a concrete artifact — a file that didn't exist proving the system remembered a past failure. Screenshot `knowledge/domain/anti-patterns.md` after Session 1, then screenshot the THINK output from Session 2 citing the AP entry.

## Open the visual guide

Open `index.html` in a browser for the full formatted guide.
