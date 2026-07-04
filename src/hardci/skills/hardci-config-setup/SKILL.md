---
name: hardci-config-setup
description: Configure HardCI as the safe local hardware-in-the-loop MCP bridge for an embedded firmware project.
metadata:
  origin: HardCI
  hardci_version: "0.1.0"
---

# HardCI Config Setup

Use HardCI as the project-local hardware gate. The policy file is `.hardci/config.yaml`.

Install and initialize from the firmware project directory:

```bash
hardci init
hardci doctor
```

Never bypass HardCI policy with raw debugger commands, direct serial device access, or direct CAN adapter access when a HardCI MCP tool is available.

If any HardCI tool returns `permission_denied`, stop and ask the user before changing policy.
