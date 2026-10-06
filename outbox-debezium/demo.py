"""Dual write vs transactional outbox. sqlite stands in for Postgres; the relay stands in for Debezium."""
import sqlite3

broker = []  # stands in for a Kafka topic


def setup():
    db = sqlite3.connect(":memory:")
    db.executescript("""
    create table orders(id integer primary key, item text);
    create table outbox(id integer primary key autoincrement, topic text, payload text, published int default 0);
    """)
    return db


def dual_write(db, oid, crash_after_db):
    db.execute("insert into orders values (?, 'book')", (oid,))
    db.commit()
    if crash_after_db:
        raise RuntimeError("process died between DB commit and broker publish")
    broker.append(("orders", f"order-created:{oid}"))


def outbox_write(db, oid, crash_after_db):
    with db:  # one local transaction: business row + event row
        db.execute("insert into orders values (?, 'book')", (oid,))
        db.execute("insert into outbox(topic, payload) values ('orders', ?)", (f"order-created:{oid}",))
    if crash_after_db:
        raise RuntimeError("process died after commit")


def relay(db):  # Debezium tails the WAL; here we poll the table
    for oid, topic, payload in db.execute("select id, topic, payload from outbox where published=0").fetchall():
        broker.append((topic, payload))
        db.execute("update outbox set published=1 where id=?", (oid,))
    db.commit()


db = setup()
try:
    dual_write(db, 1, crash_after_db=True)
except RuntimeError:
    pass
lost = db.execute("select count(*) from orders where id=1").fetchone()[0] == 1 and not broker
print("dual write: order saved, event lost =", lost)
assert lost

try:
    outbox_write(db, 2, crash_after_db=True)
except RuntimeError:
    pass
relay(db)
assert broker == [("orders", "order-created:2")]
print("outbox: event delivered after crash =", broker[0][1])
