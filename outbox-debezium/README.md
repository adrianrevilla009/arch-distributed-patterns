# outbox-debezium

A sqlite demo of a lost event versus a transactional outbox, plus a compose stack (Postgres, Kafka, Debezium Connect) with a connector config for the real setup.

## Goal

Show that "write to the database, then publish to the broker" is a dual write that can lose an event, and that writing the event into an outbox table in the same transaction fixes it.

## Run it

```
python3 demo.py
```

Expected output:

```
dual write: order saved, event lost = True
outbox: event delivered after crash = order-created:2
```

Real stack (not run end to end, see below):

```
docker compose up -d
curl -X POST -H 'Content-Type: application/json' --data @connector.json localhost:8083/connectors
docker compose down -v
```

## What it proves

- In `demo.py`, a crash between the database commit and the broker publish leaves order 1 saved and nothing in the broker.
- With `outbox_write`, the order row and the outbox row commit together; after a crash the `relay` function still publishes `order-created:2`.
- `init.sql` and `connector.json` show the Postgres side: an `outbox` table, and a Debezium `EventRouter` that routes rows by `type`.

## Trade-offs

- Delivery is at-least-once: a relay that dies after publishing and before marking the row can publish twice, so consumers must be idempotent (see `idempotent-consumer`).
- Debezium adds Kafka Connect and logical replication to operate; the polling relay in `demo.py` is simpler but adds latency and query load.
- The outbox table grows and needs cleanup.

## When not to use it

- When losing an occasional event is acceptable.
- When the broker itself is the system of record and there is no database write to keep consistent.

Not run end to end: `demo.py` uses sqlite and a polling loop as stand-ins for Postgres and Debezium. `compose.yaml` and `connector.json` were not started here, so the pinned image versions and connector settings are unverified. The password `lab` is a throwaway local value.
