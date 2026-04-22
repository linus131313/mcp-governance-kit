# The paper

The full companion paper is archived in the repository at
[`paper/governance-speed-gap.pdf`](https://github.com/linus131313/mcp-governance-kit/blob/main/paper/governance-speed-gap.pdf).

## Abstract

A typical developer agent configured with the Model Context Protocol
(MCP) scores 13.5 on the Tool Graph Capability Score introduced in the
paper, 1.9× the score of a traditional database-administration-plus-shell
tool; a full-stack developer configuration scores 49.5, 3.3× that of a
domain-administrator workstation and 7.1× the database-administration
tool. These comparisons hold under all 48 reweightings tested in a
sensitivity analysis. The capability expansion happens outside any
change-management process: MCP allows language-model hosts to bind
external tools at runtime, a property no AI-specific governance
framework in applicable form yet addresses.

The paper quantifies the gap between the adoption curve of agentic tool
binding and the response cadence of the three governance regimes CISOs
rely on, identifies six control breakpoints where application-centric
controls fail under an MCP-native architecture, and concludes that
closing the gap requires a new primitive — runtime capability-state
attestation — that no published revision yet defines.

**This repository implements that primitive.**

## Citation

See [`paper/CITATION.cff`](https://github.com/linus131313/mcp-governance-kit/blob/main/paper/CITATION.cff)
for a machine-readable citation. BibTeX equivalent:

```bibtex
@article{teklenburg2026mcp,
  title  = {The {MCP} Governance Gap: Empirical Evidence on Dynamic
            Tool Binding in Enterprise {AI}},
  author = {Teklenburg, Linus},
  year   = {2026},
  month  = {4},
  note   = {Independent Researcher},
  url    = {https://github.com/linus131313/mcp-governance-kit/blob/main/paper/governance-speed-gap.pdf}
}
```
