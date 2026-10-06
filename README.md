# arch-distributed-patterns

Seven small, runnable demos of the patterns that keep data consistent across services (outbox, sagas, idempotent consumers, strangler fig), each one failing on purpose so you can see why the pattern exists. They share a tiny Orders domain.

## What is inside

| Folder | What it shows | Run |
| --- | --- | --- |
| [`outbox-debezium`](./outbox-debezium) | A dual write that loses an event, fixed by a transactional outbox; compose stack for Postgres, Kafka and Debezium | `python3 demo.py` |
| [`saga-orchestrated`](./saga-orchestrated) | One coordinator runs steps in order and compensates in reverse after a payment failure | `python3 saga.py` |
| [`saga-choreographed`](./saga-choreographed) | The same flow with services reacting to events on a bus, no coordinator | `python3 saga.py` |
| [`idempotent-consumer`](./idempotent-consumer) | A naive increment versus a keyed upsert under redelivery | `python3 consumer.py` |
| [`inbox-dedup`](./inbox-dedup) | An inbox table that records the message id in the same transaction as the effect | `python3 inbox.py` |
| [`strangler-fig`](./strangler-fig) | A facade that routes migrated paths to a new service and the rest to legacy | `python3 router.py` |
| [`two-phase-commit-vs-saga`](./two-phase-commit-vs-saga) | What other readers see, and what is locked, under 2PC versus a saga | `python3 compare.py` |

## Prerequisites

- Python 3.10 or newer (standard library only; sqlite3 is built in).
- Docker with Compose, only for the real stack in `outbox-debezium`.

## How to read it

Start with `outbox-debezium`, then the two saga folders, then `idempotent-consumer` and `inbox-dedup`, which handle the duplicates that at-least-once delivery produces. Every demo is a single script that asserts its own result; run it from inside its folder.
