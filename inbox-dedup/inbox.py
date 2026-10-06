"""Inbox table: record the message id and apply the effect in the same transaction, so redelivery is skipped."""
import sqlite3

db = sqlite3.connect(":memory:")
db.executescript("""
create table inbox(message_id text primary key);
create table balance(account text primary key, amount int);
insert into balance values ('acc1', 100);
""")
emails_sent = []


def handle(message_id, credit):
    try:
        with db:  # inbox insert + effect commit or roll back together
            db.execute("insert into inbox values (?)", (message_id,))
            db.execute("update balance set amount = amount + ? where account='acc1'", (credit,))
    except sqlite3.IntegrityError:
        return "duplicate-skipped"
    emails_sent.append(message_id)  # non-idempotent side effect, only reached once per id
    return "applied"


if __name__ == "__main__":
    results = [handle("m1", 10), handle("m1", 10), handle("m2", 5), handle("m1", 10)]
    total = db.execute("select amount from balance").fetchone()[0]
    print(results, "balance =", total, "emails =", len(emails_sent))
    assert results == ["applied", "duplicate-skipped", "applied", "duplicate-skipped"]
    assert total == 115 and len(emails_sent) == 2
