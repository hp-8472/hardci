# HardCI Agent Instructions

This file is for AI coding agents.

HardCI is the hardware gate. The project-local `.hardci/config.yaml` is the policy.

## Human vs Agent Docs

Humans should start with:

- `README.md`
- `TROUBLESHOOTING.md`

Agents should use:

- `AGENTS.md`
- `AI_AGENT_QUICKSTART.md`
- `src/hardci/skills/hardci-config-setup/SKILL.md`

Follow `AI_AGENT_QUICKSTART.md` for installation and first-time setup. All normal setup paths are user-local and require no administrator privileges.

## Installation Model

Do not clone, checkout, or vendor the HardCI source tree into a firmware project for normal setup. Use the Python package from PyPI or the Git repository as a package source.

When the user says something like:

```text
Install https://github.com/hp-8472/hardci for this firmware project.
```

follow this model:

1. Distinguish the firmware project from the HardCI source repository.
2. Make the `hardci` CLI available user-locally.
3. Install or update the agent setup skill with `hardci skill-install --agent <agent>`.
4. Return to the firmware project directory.
5. Create or update the local `.hardci/config.yaml` without overwriting existing policy unless explicitly asked.
6. Validate with `hardci doctor`.
7. Add or merge the MCP entry in the user's MCP/client config when possible; use project `.mcp.json` only when the client needs project discovery.
8. Use HardCI MCP tools for hardware actions.

Preferred user-local install methods for agents:

- Use an existing `hardci` command when `hardci --version` works.
- Use `pipx install hardci` for a persistent isolated CLI when `pipx` is available.
- Use `uv tool install hardci` when `uv` is already available or when `pipx` is not suitable.
- Use a dedicated virtual environment under `~/.local/share/hardci/venv` as the plain Python fallback.

`uv` is not required. Do not install `uv` just because it is mentioned in older examples if `pipx` or a local venv is the simpler available route.

Never use `sudo pip`, `pip install --break-system-packages`, or system Python package writes. Avoid `python -m pip install --user hardci` as the primary recommendation because PEP 668 distributions may reject it and it is less isolated than `pipx` or a venv.

## Project Bootstrap

Run setup from the firmware project directory:

```bash
hardci init
hardci doctor
```

If `.hardci/config.yaml` already exists, preserve policy decisions and edit only project-specific values. Do not run `hardci init --force` unless the user explicitly asks for a reset. Do not stage or commit `.hardci/config.yaml` unless the user explicitly asks for a shared sanitized policy file.

If `.mcp.json` already exists, merge a `hardci` server entry and preserve existing servers. Do not overwrite existing MCP configuration with `hardci mcp-config --force` unless explicitly asked. Do not commit absolute user paths such as `/home/.../.local/bin/hardci` to project files; those belong in the user's MCP/client config.

For opencode, `opencode.json` uses its own `mcp` shape with a `type: "local"` entry and a command array. Do not paste `.mcp.json`'s `mcpServers` shape into `opencode.json`.

## MCP Visibility And Fallback

For board, PCB, flash, reset, serial, CAN, adapter, or hardware unit-test tasks, look for HardCI before using hardware tools directly:

1. Check whether a HardCI MCP tool namespace is available.
2. If not, run `hardci doctor` from the firmware project directory and inspect `.hardci/config.yaml`.
3. If MCP config was just added or changed, tell the user the agent client must be restarted before MCP tools appear in the running session.
4. For one-shot, stateless hardware actions while MCP is unavailable, use the policy-gated CLI fallback: `hardci call <tool> --args '{...}'`.
5. Do not use `hardci call` for session tools such as COM/CAN/debug sessions; use MCP, or `hardci com-stdio --config .hardci/config.yaml --port <port_id>` only for a single configured serial stream when that is explicitly needed.

Examples:

```bash
hardci call probe_target --config .hardci/config.yaml
hardci call flash_firmware --config .hardci/config.yaml --args '{"image_path":"build/firmware.elf"}'
hardci call reset_target --config .hardci/config.yaml --args '{"mode":"run"}'
```

The fallback is still HardCI and still policy-gated. Raw OpenOCD, arbitrary debugger shells, direct serial-device access, direct CAN-adapter access, and direct test-adapter access remain bypasses.

## Configuration Rules

Use `hardci init` to create the starter config, then edit only values that can be inferred from project files, detected hardware, or the user's instructions. If board, debugger, COM port, CAN bus, debug-adapter IP, or artifact path cannot be inferred, ask one concise question instead of guessing. COM ports, CAN interfaces, probe IDs, and debug-adapter IP addresses belong in `.hardci/config.yaml` because different firmware checkouts can use different hardware, but the file remains local by default.

Safe first path unless the project clearly says otherwise:

- Board: STM32 Nucleo-F446RE
- Debug probe: ST-Link
- Debug backend: OpenOCD
- OpenOCD interface config: `interface/stlink.cfg`
- OpenOCD target config: `target/stm32f4x.cfg`
- Firmware artifact root: `build/`
- Firmware artifact formats: `.elf`, `.hex`, `.bin`

Do not add firmware extensions such as `.srec` just because the build emits them. Use `.elf`, `.hex`, or `.bin` unless the user asks for another format and the selected backend supports it.

Do not enable these unless the user explicitly understands the risk and asks for a policy change:

```yaml
permissions:
  allow_raw_debugger_commands: true
  allow_mass_erase: true
```

## Hardware Workflow

Use this loop for firmware tasks:

1. Build firmware.
2. Check debugger availability with `debugger_info` if setup is unclear.
3. Probe with `probe_target` before flashing.
4. Flash only validated artifacts with `flash_firmware`.
5. Reset only when needed or requested.
6. Use configured COM, CAN, and adapter IDs through HardCI MCP tools.
7. Read the structured result and `get_last_report`.
8. Diagnose failures with `classify_last_error`.

Use HardCI MCP tools for hardware actions. Do not bypass them with raw OpenOCD commands, arbitrary debugger shells, direct serial-device access, direct CAN-adapter access, or direct test-adapter access when a HardCI tool is available.

If a HardCI tool returns `permission_denied`, stop. Do not loosen policy unless the user explicitly asks.

Healthy signals: `hardci doctor` returns `ok: true`, probe returns `target_detected: true`, flash returns `success_confirmed: true`, and hardware actions include `report_path` and `log_path`.
