# HardCI Agent Instructions

HardCI is the hardware gate. The project-local `.hardci/config.yaml` is the policy.

Use HardCI MCP tools for hardware actions. Do not bypass them with raw OpenOCD commands, arbitrary debugger shells, direct serial-device access, or direct CAN-adapter access when a HardCI tool is available.

If a HardCI tool returns `permission_denied`, stop. Do not loosen policy unless the user explicitly asks.

Install or update the local agent setup skill with:

```bash
hardci skill-install --agent opencode
```

For migration from AI-HIL, run:

```bash
hardci migrate-aihil
hardci doctor
```
