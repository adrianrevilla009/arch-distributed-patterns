"""Idempotent consumer by making the effect itself idempotent (absolute, keyed upsert) vs a naive increment."""
import sqlite3

# at-least-once delivery: the broker redelivers message m2
messages = [("m1", "o1", 10), ("m2", "o1", 15), ("m2", "o1", 15), ("m3", "o2", 7)]


def naive(db):
    db.execute("create table totals(order_id text, amount int)")
    for _, oid, amt in messages:
        db.execute("insert into totals values (?, ?)", (oid, amt))  # duplicate m2 adds a second row
    return db.execute("select sum(amount) from totals where order_id='o1'").fetchone()[0]


def idempotent(db):
    db.execute("create table totals(msg_id text primary key, order_id text, amount int)")
    for mid, oid, amt in messages:
        db.execute("insert or ignore into totals values (?, ?, ?)", (mid, oid, amt))  # same key, same effect
    return db.execute("select sum(amount) from totals where order_id='o1'").fetchone()[0]


if __name__ == "__main__":
    n, i = naive(sqlite3.connect(":memory:")), idempotent(sqlite3.connect(":memory:"))
    print(f"naive o1 total={n} (wrong), idempotent o1 total={i} (right)")
    assert n == 40 and i == 25
