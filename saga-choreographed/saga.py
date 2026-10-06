"""Choreographed saga: services react to each other's events on a bus; no central coordinator."""
from collections import defaultdict, deque


class Bus:
    def __init__(self):
        self.subs, self.q, self.trace = defaultdict(list), deque(), []

    def on(self, topic, fn):
        self.subs[topic].append(fn)

    def emit(self, topic):
        self.q.append(topic)

    def drain(self):
        while self.q:
            t = self.q.popleft()
            self.trace.append(t)
            for fn in self.subs[t]:
                fn()


def wire(bus, state, fail_payment):
    def reserve():
        state["stock"] -= 1
        bus.emit("StockReserved")

    def charge():
        if fail_payment:
            bus.emit("PaymentFailed")
        else:
            state["paid"] = True
            bus.emit("PaymentCharged")

    def release():  # stock service compensates on its own, reacting to the failure event
        state["stock"] += 1
        bus.emit("OrderCancelled")

    def ship():
        state["shipped"] = True

    bus.on("OrderPlaced", reserve)
    bus.on("StockReserved", charge)
    bus.on("PaymentCharged", ship)
    bus.on("PaymentFailed", release)


if __name__ == "__main__":
    for fail in (False, True):
        bus, state = Bus(), {"stock": 5, "paid": False, "shipped": False}
        wire(bus, state, fail)
        bus.emit("OrderPlaced")
        bus.drain()
        print("fail" if fail else "ok  ", "->", " > ".join(bus.trace))
        if fail:
            assert state == {"stock": 5, "paid": False, "shipped": False} and bus.trace[-1] == "OrderCancelled"
        else:
            assert state == {"stock": 4, "paid": True, "shipped": True}
