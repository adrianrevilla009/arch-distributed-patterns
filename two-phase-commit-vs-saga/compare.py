"""2PC vs saga when one participant fails. Counts what other transactions see and how long locks are held."""


class Resource:
    def __init__(self, name, fail=False):
        self.name, self.fail, self.value, self.locked = name, fail, "before", False

    def prepare(self):
        self.locked = True  # 2PC: lock held until the coordinator decides
        return not self.fail

    def commit(self, v="after"):
        self.value, self.locked = v, False

    def rollback(self):
        self.locked = False


def two_phase(rs):
    votes = [r.prepare() for r in rs]
    locked_during_vote = all(r.locked for r in rs)
    if all(votes):
        [r.commit() for r in rs]
    else:
        [r.rollback() for r in rs]
    return locked_during_vote


def saga(rs):
    visible = []  # intermediate states other readers could observe
    done = []
    for r in rs:
        if r.fail:
            for d in reversed(done):
                d.commit("before")  # compensation
            return visible
        r.commit()  # local commit, no lock kept
        done.append(r)
        visible.append((r.name, r.value))
    return visible


if __name__ == "__main__":
    a, b = Resource("stock"), Resource("payment", fail=True)
    locked = two_phase([a, b])
    assert locked and a.value == "before" and not a.locked
    print("2PC: all participants were locked while voting; failure left no visible change")

    a, b = Resource("stock"), Resource("payment", fail=True)
    seen = saga([a, b])
    assert seen == [("stock", "after")] and a.value == "before"
    print("saga: stock was visibly 'after' before compensation restored it:", seen)
