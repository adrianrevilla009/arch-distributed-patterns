# saga-orchestrated

An orchestrated saga in `saga.py`: a coordinator runs reserve-stock, charge-payment and ship, and compensates in reverse order on failure.

## Goal

Show how a multi-step order flow without a shared transaction is undone by explicit compensating actions, driven from one place.

## Run it

```
python3 saga.py
```

Expected output:

```
reserve-stock: ok | charge-payment: FAILED (card declined) | reserve-stock: compensated
happy path committed; deliberate payment failure compensated stock
```

## What it proves

- On the happy path the state ends as stock 4, paid, shipped (asserted in `saga.py`).
- With `fail_payment=True` the payment step raises "card declined", and stock goes back from 4 to 5.
- Only steps that completed are compensated, newest first; the failed step and later steps are not touched.

## Trade-offs

- The coordinator is a single place to read and test the flow, but it is also a component that knows every participant.
- Compensations are new business actions and not true rollbacks; other readers can see the intermediate state.
- Here the run is in memory and synchronous. A real orchestrator must persist its progress to survive a crash mid-saga.

## When not to use it

- When all steps live in one database; a local transaction is simpler and stronger.
- When a step cannot be compensated (for example an email already sent) without extra design.
