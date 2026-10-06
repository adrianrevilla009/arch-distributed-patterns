# strangler-fig

A local HTTP demo in `router.py`: a facade server forwards migrated paths to a "new" backend and all other paths to a "legacy" backend.

## Goal

Show how a legacy system can be replaced route by route behind a single entry point, without a big-bang cutover.

## Run it

```
python3 router.py
```

Expected output:

```
['new:/orders/1', 'legacy:/customers/9']
```

## What it proves

- Three `HTTPServer` instances start on random local ports: legacy, new and the facade.
- A request for `/orders/1` is answered by the new service because the path starts with a prefix in `MIGRATED`.
- `/customers/9` falls through to legacy; moving a route means adding its prefix to the `MIGRATED` tuple.

## Trade-offs

- The facade is an extra hop and a single point of failure; here it is a minimal Python proxy and not a production gateway.
- Routing by prefix is the simplest rule; splitting by user or percentage needs more logic, and this demo does not do it.
- Old and new services may both need the same data during migration, which this demo does not address.
- It handles only GET and does not forward headers or status codes.

## When not to use it

- When the legacy system is small enough to rewrite in one release.
- When the system has no clear seams (paths, queues) at which to split traffic.
