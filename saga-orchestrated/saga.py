"""Orchestrated saga: one coordinator calls steps in order and runs compensations in reverse on failure."""


class Step:
    def __init__(self, name, action, compensate):
        self.name, self.action, self.compensate = name, action, compensate


def run(steps, log):
    done = []
    for s in steps:
        try:
            s.action()
            log.append(f"{s.name}: ok")
            done.append(s)
        except Exception as e:
            log.append(f"{s.name}: FAILED ({e})")
            for d in reversed(done):
                d.compensate()
                log.append(f"{d.name}: compensated")
            return False
    return True


def build(state, fail_payment):
    def pay():
        if fail_payment:
            raise RuntimeError("card declined")
        state["paid"] = True

    return [
        Step("reserve-stock", lambda: state.update(stock=state["stock"] - 1), lambda: state.update(stock=state["stock"] + 1)),
        Step("charge-payment", pay, lambda: state.update(paid=False)),
        Step("ship", lambda: state.update(shipped=True), lambda: state.update(shipped=False)),
    ]


if __name__ == "__main__":
    ok_state = {"stock": 5, "paid": False, "shipped": False}
    log = []
    assert run(build(ok_state, False), log)
    assert ok_state == {"stock": 4, "paid": True, "shipped": True}

    bad_state = {"stock": 5, "paid": False, "shipped": False}
    log = []
    assert not run(build(bad_state, True), log)
    assert bad_state == {"stock": 5, "paid": False, "shipped": False}  # stock released
    print(" | ".join(log))
    print("happy path committed; deliberate payment failure compensated stock")
