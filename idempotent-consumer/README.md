# idempotent-consumer

A sqlite comparison in `consumer.py` of a naive consumer and an idempotent one when the broker redelivers a message.

## Goal

Show that at-least-once delivery corrupts totals unless the effect itself is idempotent, and make it idempotent with a keyed insert.

## Run it

```
python3 consumer.py
```

Expected output:

```
naive o1 total=40 (wrong), idempotent o1 total=25 (right)
```

## What it proves

- The message list contains `m2` twice. The naive version inserts a row per delivery, so order `o1` totals 10 + 15 + 15 = 40.
- The idempotent version uses `msg_id` as primary key with `insert or ignore`, so the repeat is a no-op and `o1` totals 25.
- The script asserts both numbers, so a regression fails loudly.

## Trade-offs

- The effect must be expressible as a keyed write; side effects such as sending an email are not covered (see `inbox-dedup`).
- Keeping one row per message grows storage; old keys need a retention policy.
- The key must be stable across redeliveries, which means the producer has to assign it.

## When not to use it

- When the effect is a non-database call that cannot be keyed.
- When exactly-once semantics are already provided end to end and verified for your path.
