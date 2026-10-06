# two-phase-commit-vs-saga

A model in `compare.py` of two participants (stock and payment) where payment fails, run once under two-phase commit and once as a saga.

## Goal

Show the core trade between the two: 2PC holds locks and exposes no intermediate state, while a saga holds no locks but lets readers see intermediate state.

## Run it

```
python3 compare.py
```

Expected output:

```
2PC: all participants were locked while voting; failure left no visible change
saga: stock was visibly 'after' before compensation restored it: [('stock', 'after')]
```

## What it proves

- In `two_phase`, both resources are locked after `prepare`, the failing vote leads to rollback, and stock still reads `before`.
- In `saga`, stock commits locally first, so a reader sees `('stock', 'after')` until the compensation sets it back to `before`.
- Both runs end with stock back at `before`; they differ in what happened in between.

## Trade-offs

- 2PC gives atomic visibility but blocks on a slow or crashed coordinator, and needs every participant to support it.
- A saga scales across services and brokers but needs compensations and tolerance for intermediate states.
- This is an in-memory model of the idea; it has no real transaction manager, timeouts or crash recovery.

## When not to use it

- As a benchmark: it counts visible states, not latency or throughput.
- As guidance for a single database, where a local transaction already gives you both.
