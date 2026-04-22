# Tool Graph Capability Score (TCS)

## Formula

Given a tool graph `G` (the set of tools bound to a host), TCS is:

$$
\mathrm{TCS}(G) = \left[ \sum_{t \in G} \mathrm{reach}(t) \cdot \mathrm{action}(t) \right] \cdot \left( 1 + t_{\mathrm{coef}} \cdot T(G) \right)
$$

where

- `reach(t)` is `local=1` or `network=2`,
- `action(t)` is `read=1`, `write=2`, or `execute=3`,
- `T(G)` is the count of third-party (non-first-party-to-the-host) servers,
- `t_coef` defaults to `0.25`.

## What TCS is, and is not

TCS is a **comparability** metric, not a safety metric. Its value is
that it is reproducible and ordinally stable: under all 48 reasonable
reweightings tested in the paper (`w_write ∈ {1.5, 2, 2.5, 3}`,
`w_execute ∈ {2, 3, 4, 5}`, `t_coef ∈ {0.1, 0.25, 0.5}`), the
comparisons that matter hold — `C4 > R4` in 48/48, `C3 > R3` in 48/48,
`C2 > R3` in 39/48. The exact ranking is preserved in 20 of the 48.

You can reproduce this analysis locally:

```bash
mcp-gov tcs sensitivity
```

## Table 3 reproduction

```bash
mcp-gov tcs reference
```

The values printed match the paper to the decimal: C1=1.0, C2=9.0,
C3=13.5, C4=49.5, C5=29.75, R1=2.0, R2=5.0, R3=7.0, R4=15.0.
