# saga-choreographed

A choreographed saga in `saga.py`: an in-memory event bus and three reactions (reserve, charge, ship) with no coordinator.

## Goal

Show the same order flow as `saga-orchestrated`, but with each service reacting to events and compensating on its own.

## Run it

```
python3 saga.py
```

Expected output:

```
ok   -> OrderPlaced > StockReserved > PaymentCharged
fail -> OrderPlaced > StockReserved > PaymentFailed > OrderCancelled
```

## What it proves

- The `Bus` in `saga.py` queues events and calls subscribers; the flow emerges from `bus.on(...)` wiring alone.
- On the happy path the state ends as stock 4, paid, shipped.
- On a declined payment, the stock handler reacts to `PaymentFailed`, returns stock to 5 and emits `OrderCancelled`; the script asserts this.

## Trade-offs

- No central point of failure and loose coupling, but the overall flow is only visible by reading every subscription.
- Adding a step means touching several handlers, and cyclic event chains are easy to create.
- The bus here is in memory and single process; a real broker brings redelivery and ordering concerns that this demo does not cover.

## When not to use it

- When the flow has many steps or branches that need to be read and audited in one place; use an orchestrator.
- When you need a clear answer to "where is this order now?" without tracing events.
