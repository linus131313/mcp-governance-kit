# Policy authoring

A policy is a YAML document that parameterises the six breakpoint checks.
The schema is defined in `mcp_governance_kit.policy.Policy` and validates
on load.

## Minimal example

```yaml
version: 1
name: my-team
max_tcs: 20
max_third_party: 5
third_party_allowlist:
  - "@modelcontextprotocol/server-github"
  - "@modelcontextprotocol/server-filesystem"
```

## Full reference

| Field | Type | Meaning |
|-------|------|---------|
| `version` | int | Schema version; default 1. |
| `name` | string | Human name; shown in the policy report. |
| `max_tcs` | float? | If TCS exceeds, B4 blocks. |
| `warn_tcs` | float? | If TCS exceeds, B4 warns. |
| `max_third_party` | int? | If exceeded, B2 blocks. |
| `third_party_allowlist` | string[] | Identities not on the list trigger B2 warn. |
| `require_approval_for_execute` | bool | B4 blocks when network+execute tools are bound without approval. |
| `execute_approved` | bool | Set to lift the B4 block when approval has been obtained. |
| `require_approval_for_changes` | bool | B1 blocks on any change without an approval flag. |
| `changes_approved` | bool | Set to lift the B1 block. |
| `allow_exfil_paths` | bool | If true, B3 downgrades warn to info. |

## Three built-in policies

| Policy | Intended role | Highlights |
|--------|---------------|------------|
| `default.yaml` | Starting point for most teams | TCS ≤ 30, warn at 15. |
| `developer.yaml` | Full-stack engineering | TCS ≤ 20, allow-list covers git/shell/docker. |
| `restricted.yaml` | Analyst / data-science | TCS ≤ 10, execute requires approval. |
