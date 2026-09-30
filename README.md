# Encore

You're building the backend for a small live-event box office. Ticket prices
change by campaign, every cart edit made over the phone has to be reversible,
and sold-out fans who join a waitlist need to hear back the moment seats open
up again.

## Business requirements

- Ticket prices change by campaign: early-bird discounts before a show,
  group discounts for large parties. Staff need to switch the active pricing
  algorithm on a cart without rewriting the checkout math.
- Every cart edit made during a phone order must be reversible. If staff
  misclick, or a customer changes their mind, adding, removing, or
  re-pricing tickets needs a clean undo (and redo).
- When a show sells out, fans can join a waitlist. The moment seats free up
  again, everyone on the waitlist must be notified automatically, but only
  when the show actually goes from sold out to available, not on every
  capacity tweak.

## Architecture

- **Strategy**: `StandardPricing`, `EarlyBirdPricing`, and `GroupPricing` are
  interchangeable `PricingStrategy` implementations that turn a cart's
  subtotal into its final total.
- **Command**: `AddTicketCommand`, `RemoveTicketCommand`, and
  `SetPricingStrategyCommand` encapsulate cart edits so `CartInvoker` can
  run, undo, and redo them.
- **Observer**: `Show` notifies subscribed `WaitlistObserver`s
  (`EmailWaitlistNotifier`, `SMSWaitlistNotifier`) only when it transitions
  from sold out to having seats again.

## Project layout

```dir_tree
root_dir
├─ encore/
│  ├─ __init__.py
│  ├─ pricing.py
│  ├─ cart.py
│  ├─ waitlist.py
│  └─ app.py
├─ tests/
│  ├─ test_pricing.py
│  ├─ test_cart.py
│  └─ test_waitlist.py
└─ README.md
```

## Setup

Preferred: [uv](https://docs.astral.sh/uv/). Install uv once per machine (see
uv's docs), then from inside your local clone:

```bash
uv venv                              # create a local virtual environment (.venv)
uv pip install -r requirements.txt   # install pytest into it
```

From then on, run any Python command through `uv run` so it uses that
environment automatically:

```bash
uv run pytest -q                     # run all tests
uv run pytest ./tests/test_pricing.py   # run pricing tests only
uv run python -m encore.app          # run the demo app
```

<details>
<summary>Alternative: plain venv + pip</summary>

```bash
# Unix
python -m venv .venv && source .venv/bin/activate

# Windows:
python -m venv .venv
.venv\Scripts\activate

pip install -r requirements.txt

python -m pytest -q
python -m pytest ./tests/test_pricing.py
python -m encore.app
```

</details>

## How to submit

Two different repos are involved, so be precise about which is which:

- **The course repo** is `ami232/sdd-behavioral-patterns`.
  This is where your work has to end up. You cannot push to it, which is
  exactly why you send a pull request.
- **Your fork** is `<your-github-username>/sdd-behavioral-patterns`.
  This is where you do the work.

Every step below says which of the two it means. Where these instructions say
"the course repo", they never mean your fork, even though your fork contains
a copy of this same README.

1. Fork `ami232/sdd-behavioral-patterns` to your own GitHub account.
   Keep the fork **public** (the default when forking a public repo) so it can
   be reviewed without needing collaborator access.
2. Clone **your fork**, not the course repo, and work through the exercises
   below on a branch:

   ```bash
   git clone <the URL from the green "Code" button on your fork>
   cd sdd-behavioral-patterns
   git switch -c solution
   ```

3. Commit your changes and push the branch to your fork:

   ```bash
   git push origin solution
   ```

4. Open a **pull request from your fork into the course repo**. On github.com,
   open your fork, click "Contribute", then "Open pull request".

   Before you submit it, check that the pull request header reads exactly:

   | Field | Value |
   | --- | --- |
   | base repository | `ami232/sdd-behavioral-patterns` |
   | base | `main` |
   | head repository | `<your-github-username>/sdd-behavioral-patterns` |
   | compare | `solution` |

   **If your own username appears on both sides, the pull request is aimed at
   your own fork and will never reach us.** Change it with the "base
   repository" dropdown before submitting.
5. Opening the PR automatically runs the full test suite as a GitHub Actions
   check, see the "Checks" tab on your PR. All three test files
   (`test_pricing.py`, `test_cart.py`, `test_waitlist.py`) must pass for the
   check to go green.
6. Submit the link to your pull request on Blackboard. This is your
   submission; the green check confirms the tests pass, but the PR itself
   (with your commits and diff) is what gets graded.

## Exercises

### 1. Implement the pricing strategies

Functional requirements:

- `StandardPricing.price(subtotal, quantity)` returns `subtotal` unchanged.
- `EarlyBirdPricing(percent)` must raise `ValueError` when constructed if
  `percent` isn't between 0 and 100 (inclusive). `price(subtotal, quantity)`
  applies that percentage discount to `subtotal`.
- `GroupPricing(threshold, per_ticket_off).price(subtotal, quantity)`
  subtracts `per_ticket_off * quantity` from `subtotal`, but only once
  `quantity >= threshold`; below the threshold it returns `subtotal`
  unchanged.
- No strategy may ever return a negative total; clamp the result at `0.0`.

To test this part:

```bash
uv run pytest ./tests/test_pricing.py
```

Goal --> Pass pricing tests

### 2. Implement the ticket cart commands

Functional requirements:

- `AddTicketCommand.execute()` adds `qty` tickets of `category` at
  `unit_price` to the cart; `undo()` removes exactly that quantity again.
- `RemoveTicketCommand.execute()` removes up to `qty` tickets of `category`
  (the cart may hold fewer) and must remember how many were actually
  removed, and at what price, so `undo()` can restore precisely that.
- `SetPricingStrategyCommand.execute()` swaps the cart's active
  `PricingStrategy`, remembering the previous one so `undo()` can restore
  it.
- `CartInvoker.run(command)` executes a command and records it in history,
  clearing any pending redo stack.
- `CartInvoker.undo(n)` / `redo(n)` undo/redo up to `n` commands and return
  how many were actually undone/redone (fewer than `n` once history runs
  out).

To test this part:

```bash
uv run pytest ./tests/test_cart.py
```

Goal --> Pass cart tests

### 3. Implement the waitlist notifications

Functional requirements:

- `Show.join_waitlist(observer)` / `leave_waitlist(observer)`
  subscribe/unsubscribe a `WaitlistObserver`.
- `Show.release_seats(count)` raises `ValueError` for a non-positive `count`.
  Otherwise it increases `available_seats`, and notifies every subscribed
  observer (via `notify(title, available_seats)`) **only** when the show
  transitions from zero available seats to some available seats. Releasing
  seats on a show that already had seats available must not notify anyone.
- `EmailWaitlistNotifier.notify()` and `SMSWaitlistNotifier.notify()` each
  append a formatted message to their own `sent` list.
- An observer that has left the waitlist must never be notified again.

To test this part:

```bash
uv run pytest ./tests/test_waitlist.py
```

Goal --> Pass waitlist tests
