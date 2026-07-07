---
name: hardci-config-setup
description: HardCI hardware-in-the-loop setup and board actions: use when configuring HardCI, flashing/probing/resetting embedded targets, reading configured serial/CAN/test adapters, or running firmware/unit tests on PCB/board via MCP.
metadata:
  origin: HardCI
  hardci_version: "0.2.0"
---

# HardCI Config Setup

Use HardCI as the project-local hardware gate. The policy file is `.hardci/config.yaml`.

Load this skill for embedded hardware actions, not only for first-time setup. Triggers include PCB, board, target, flash, reset, ST-Link, OpenOCD, pyOCD, STM32CubeProgrammer, serial/UART, CAN, test adapter, hardware-in-the-loop, and running firmware or unit tests on real hardware.

HardCI setup is split by audience:

- Humans start with `README.md` and `TROUBLESHOOTING.md`.
- Agents follow `AGENTS.md`, `AI_AGENT_QUICKSTART.md`, and this skill.

Install or locate the CLI user-locally. `uv` is optional; use `pipx install hardci`, `uv tool install hardci`, or a dedicated venv under `~/.local/share/hardci/venv`. Never use `sudo pip` or `pip install --break-system-packages`.

Initialize from the firmware project directory:

```bash
hardci init
hardci doctor
```

If `.hardci/config.yaml` already exists, preserve it and edit only project-specific values. Do not run `hardci init --force` unless the user explicitly asks. Do not stage or commit `.hardci/config.yaml` unless the user explicitly asks for a shared sanitized policy file.

If `.mcp.json` already exists, merge a `hardci` MCP server entry and preserve existing servers. Put absolute user paths such as `/home/.../.local/bin/hardci` in the user's MCP/client config when possible; keep project MCP files portable. For opencode, use `opencode.json`'s `mcp` shape with `type: "local"` and a command array; do not paste `.mcp.json`'s `mcpServers` object into `opencode.json`.

COM ports, CAN interfaces, probe IDs, and debug-adapter IP addresses belong in `.hardci/config.yaml` because they describe the hardware assignment for this firmware checkout. The config remains local by default.

If the running agent session does not expose HardCI MCP tools, run `hardci doctor` from the firmware project directory. If MCP config was just added or changed, tell the user to restart the agent client. For one-shot stateless actions while MCP is unavailable, use the policy-gated fallback:

```bash
hardci call probe_target --config .hardci/config.yaml
hardci call flash_firmware --config .hardci/config.yaml --args '{"image_path":"build/firmware.elf"}'
hardci call reset_target --config .hardci/config.yaml --args '{"mode":"run"}'
```

Do not use `hardci call` for session tools such as COM/CAN/debug sessions; use MCP, or `hardci com-stdio --config .hardci/config.yaml --port <port_id>` only for a single configured serial stream when explicitly needed.

Use `.elf`, `.hex`, or `.bin` firmware artifacts unless the user asks for another format and the configured debugger backend supports it. Do not add `.srec` just because a build directory contains it.

Never bypass HardCI policy with raw debugger commands, direct serial device access, or direct CAN adapter access when a HardCI MCP tool is available.

If any HardCI tool returns `permission_denied`, stop and ask the user before changing policy.
