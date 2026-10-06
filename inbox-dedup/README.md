# inbox-dedup

An inbox table in `inbox.py`: the message id and the balance update are written in one sqlite transaction, and a repeated id is skipped.

## Goal

Show how to deduplicate redelivered messages, including ones with non-idempotent side effects, by recording the id atomically with the effect.

## Run it

```
python3 inbox.py
```

Expected output:

```
['applied', 'duplicate-skipped', 'applied', 'duplicate-skipped'] balance = 115 emails = 2
```

## What it proves

- `handle("m1", 10)` is delivered three times in total but credits the account only once; the second insert of the id raises `IntegrityError` and is skipped.
- The balance goes 100 + 10 + 5 = 115, and the simulated email list has two entries, not four.
- The inbox insert and the update share one `with db:` block, so they commit or roll back together.

## Trade-offs

- Dedup and effect must share one transactional store; an effect in another system is not covered.
- In this demo the email is appended after the commit. A crash between the two would drop it, so a real design would also put the email in an outbox.
- The inbox table grows and needs pruning.

## When not to use it

- When the effect is already idempotent by key (see `idempotent-consumer`).
- When the consumer has no database to hold the inbox table.
