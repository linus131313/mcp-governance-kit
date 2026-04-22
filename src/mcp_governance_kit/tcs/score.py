"""The pure TCS scoring function.

    TCS(G) = [ sum_{t in G} reach(t) * action(t) ] * (1 + t_coef * T(G))

where ``T(G)`` is the number of third-party servers in the tool graph.
The function is deterministic and has no side effects — it can be safely
invoked on untrusted input.
"""

from __future__ import annotations

from mcp_governance_kit.tcs.models import Action, Config, Reach
from mcp_governance_kit.tcs.weights import DEFAULT_WEIGHTS, Weights


def tcs(config: Config, weights: Weights | None = None) -> float:
    """Compute the Tool Graph Capability Score for ``config``.

    Parameters
    ----------
    config:
        The tool graph to score.
    weights:
        Optional weight bundle. Defaults to the paper's published weights.

    Returns
    -------
    float
        The scalar TCS. Comparable across configurations under the same
        ``weights``.
    """
    w = weights or DEFAULT_WEIGHTS
    reach_weight = {Reach.LOCAL: w.w_local, Reach.NETWORK: w.w_network}
    action_weight = {
        Action.READ: w.w_read,
        Action.WRITE: w.w_write,
        Action.EXECUTE: w.w_execute,
    }
    base = sum(reach_weight[t.reach] * action_weight[t.action] for t in config.tools)
    return base * (1 + w.t_coef * config.third_party_count)
