"""Weight bundles for the TCS score and the 48-point reweighting grid.

The default weights are those of §5.3 of the paper:

    reach:  local=1, network=2
    action: read=1, write=2, execute=3
    transitivity coefficient: 0.25

The sensitivity grid covers ``w_write in {1.5, 2, 2.5, 3}``,
``w_execute in {2, 3, 4, 5}`` and ``t_coef in {0.1, 0.25, 0.5}``, which
yields 48 settings and reproduces the sensitivity analysis reported in
the paper.
"""

from __future__ import annotations

from itertools import product

from pydantic import BaseModel, ConfigDict, Field


class Weights(BaseModel):
    """Immutable weight bundle for a single TCS evaluation."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    w_local: float = Field(default=1.0, gt=0)
    w_network: float = Field(default=2.0, gt=0)
    w_read: float = Field(default=1.0, gt=0)
    w_write: float = Field(default=2.0, gt=0)
    w_execute: float = Field(default=3.0, gt=0)
    t_coef: float = Field(default=0.25, ge=0)


DEFAULT_WEIGHTS: Weights = Weights()


def reweighting_grid() -> list[Weights]:
    """Enumerate the 48 reweightings used in the paper's sensitivity analysis."""
    grid: list[Weights] = []
    for w_write, w_execute, t_coef in product(
        (1.5, 2.0, 2.5, 3.0),
        (2.0, 3.0, 4.0, 5.0),
        (0.1, 0.25, 0.5),
    ):
        grid.append(
            Weights(
                w_write=w_write,
                w_execute=w_execute,
                t_coef=t_coef,
            )
        )
    return grid
