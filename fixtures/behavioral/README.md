# Behavioral fixtures

Deterministic MCP refund-workflow scenarios graded without LLM judges.

| Fixture | Expected verdict |
|---------|------------------|
| `refund-without-approval` | `POLICY_VIOLATION` — sensitive tool without approval |
| `denied-action` | `POLICY_VIOLATION` — explicit deny on refund |
| `valid-refund-path` | `COMPLIANT` — approved refund with policy check |
| `valid-lookup-only` | `COMPLIANT` — read-only lookups |
| `valid-policy-check-only` | `COMPLIANT` — policy check without mutation |
| `prohibited-tool` | `PROHIBITED_TOOL` — `shell_exec` blocked |
| `execute-code-blocked` | `PROHIBITED_TOOL` — `execute_code` blocked |
| `delete-customer-blocked` | `PROHIBITED_TOOL` — destructive tool blocked |
| `malformed-refund-args` | `INVALID_TOOL_ARGS` — missing `amount_cents` |
| `empty-customer-id` | `INVALID_TOOL_ARGS` — empty required customer id |

Run:

```bash
witnessdiff run-behavioral-suite
```
