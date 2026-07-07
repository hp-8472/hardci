# AI Agent Quickstart

Use HardCI as the local MCP server for embedded firmware development and embedded hardware actions.

This file is for agents. Humans should start with `README.md` and use `TROUBLESHOOTING.md` for operator-facing diagnostics.

If you were given only the HardCI repository URL and asked to set it up, do not clone or vendor the repository into the firmware project. Install the Python package user-locally, use that installed package to generate skill and MCP files, configure the firmware project, validate with `hardci doctor`, then return to the firmware task.

## Ground Rules

- Never use `sudo` or administrator privileges for HardCI installation.
- Never use `pip install --break-system-packages` or write into the system Python.
- Prefer an existing user-local `hardci` command, `pipx`, `uv`, or a dedicated user-local venv.
- If board, debugger, COM port, CAN bus, or artifact path cannot be inferred, ask one concise question instead of guessing.
- Preserve existing `.hardci/config.yaml`, `.mcp.json`, and `opencode.json` entries unless the user explicitly asks to replace them.

## Make The CLI Available

Use the first working option. Keep the resolved command in mind as `HARDCI`; use an absolute path in MCP configs if the command may not be on `PATH`.

1. Existing install:

```bash
hardci --version
```

2. Persistent isolated install with `pipx`:

```bash
pipx install hardci
hardci --version
```

3. Persistent isolated install with `uv` when `uv` is already available:

```bash
uv tool install hardci
hardci --version
```

4. Plain Python fallback without `pipx` or `uv`:

```bash
python3 -m venv ~/.local/share/hardci/venv
~/.local/share/hardci/venv/bin/python -m pip install --upgrade pip
~/.local/share/hardci/venv/bin/python -m pip install hardci
mkdir -p ~/.local/bin
ln -sf ~/.local/share/hardci/venv/bin/hardci ~/.local/bin/hardci
~/.local/bin/hardci --version
```

5. Use the GitHub repository as package source only when the PyPI package is unavailable or the user explicitly asked for the repository version:

```bash
pipx install git+https://github.com/hp-8472/hardci
# or: uv tool install git+https://github.com/hp-8472/hardci
```

`uv` is optional. It is useful for fast package execution and isolated tool installs, but it is not a HardCI requirement.

Avoid `python -m pip install --user hardci` as the default route. It can work on unmanaged Python installations, but PEP 668 distributions often reject it, and it is less isolated than `pipx` or a dedicated venv.

## Corporate TLS

If `uv` fails with `invalid peer certificate: UnknownIssuer`, retry with system certificates:

```bash
UV_SYSTEM_CERTS=1 uvx hardci --version
uv --system-certs tool install hardci
```

If `pipx` or `pip` fails with certificate errors, report the certificate issue and ask the user which corporate CA/certificate configuration should be used. Do not disable TLS verification silently.

## Generate Agent Files

After the CLI is available, generate or update agent files through the HardCI package. Do not hand-write these files during normal installation.

```bash
hardci skill-install --agent <agent>
hardci mcp-install --agent <agent>
```

Supported skill agent names and aliases: `opencode`/`open-code`, `claude-code`/`claude`, `codex`/`codex-cli`/`openai-codex`. For other skill-capable agents use `--agent <name> --target <path>` with that agent's documented user-level skill directory.

Supported MCP install targets: `opencode`, `claude-code`, `codex`, and `mcp-json` for a generic `.mcp.json` file when the client needs project discovery:

```bash
hardci mcp-install --agent mcp-json --target .mcp.json
```

For opencode, tell the user to restart opencode after skill or MCP config changes.

## Configure Each Project

Run these commands from the firmware project directory, not from the HardCI source repository:

```bash
hardci init
# edit .hardci/config.yaml for the target, debugger, artifact roots, and approved IO
hardci doctor
```

If `.hardci/config.yaml` already exists, do not overwrite it. Edit only the fields required for the current setup. Do not stage or commit `.hardci/config.yaml` unless the user explicitly asks for a shared sanitized policy file.

Reference first path unless the project or user clearly says otherwise:

- STM32 Nucleo-F446RE.
- ST-Link with OpenOCD.
- `interface/stlink.cfg` and `target/stm32f4x.cfg`.
- Python 3.10 or newer.
- Firmware artifacts under `build/`.
- Firmware artifact formats `.elf`, `.hex`, and `.bin`.

Do not add `.srec` or other extensions just because a build directory contains them. Add only formats the user wants to flash and the selected debugger backend supports.

Use `hardci com-ports` to discover serial devices. Configure a COM port only when it is clearly the DUT UART or the user confirms it. Keep COM ports, CAN interfaces, probe IDs, and debug-adapter IP addresses in `.hardci/config.yaml` because they are project-checkout hardware assignments, but keep that config local by default. If multiple probes or serial devices are present, set `debugger.probe_id` and ask when selection is ambiguous.

Expected healthy `hardci doctor` result: `ok: true`, `summary: "HardCI configuration loaded and debugger checked."`, and a nested debugger result with `ok: true`.

## Configure MCP

MCP config is launcher config. Prefer the user's MCP/client configuration for platform-dependent values such as absolute executable paths. `.mcp.json` is only needed when the MCP client discovers servers from the project. Generate MCP entries with `hardci mcp-install`; use `hardci mcp-config --output .mcp.json` only for the legacy portable project file.

If `.mcp.json` already exists, merge this server entry instead of overwriting the file:

```json
{
  "mcpServers": {
    "hardci": {
      "command": "hardci",
      "args": ["mcp-stdio", "--config", ".hardci/config.yaml"]
    }
  }
}
```

If the MCP client may not inherit `PATH`, use the absolute user-local executable path, for example `/home/<user>/.local/bin/hardci`, in the user's MCP/client config. Do not commit that path to project files.

For opencode, use `opencode.json`'s native `mcp` shape instead of `.mcp.json`'s `mcpServers` shape:

```json
{
  "mcp": {
    "hardci": {
      "type": "local",
      "command": ["/home/<user>/.local/bin/hardci", "mcp-stdio", "--config", ".hardci/config.yaml"],
      "cwd": ".",
      "enabled": true,
      "timeout": 120000
    }
  }
}
```

`mcp-stdio` is project-scoped and JSON-RPC only. Do not add `--port` to `mcp-stdio`. For a continuous plain-text serial channel use a separate `hardci com-stdio --config .hardci/config.yaml --port <port_id>` process only when the user explicitly wants it.

## If MCP Tools Are Not Visible

If the running agent session does not expose HardCI MCP tools, do not fall back to raw OpenOCD, direct serial devices, direct CAN adapters, or direct test adapters.

1. Run `hardci doctor` from the firmware project directory.
2. Confirm `.hardci/config.yaml` exists and the MCP entry points to `hardci mcp-stdio --config .hardci/config.yaml`.
3. If the MCP entry or opencode config was just created or changed, tell the user to restart the agent client. Existing sessions usually do not hot-load new MCP servers.
4. For one-shot stateless hardware actions before restart, use `hardci call` so the same project policy still gates the operation.

Examples:

```bash
hardci call probe_target --config .hardci/config.yaml
hardci call flash_firmware --config .hardci/config.yaml --args '{"image_path":"build/firmware.elf"}'
hardci call reset_target --config .hardci/config.yaml --args '{"mode":"run"}'
```

`hardci call` starts a fresh process for a single tool call. It intentionally rejects session-based tools such as `com_session_start`, `can_session_start`, and `debug_start_session` with `stateful_tool_requires_mcp`. Use MCP for those, or `hardci com-stdio --config .hardci/config.yaml --port <port_id>` for one configured serial stream when the user explicitly needs a plain-text serial relay.

## Use The Tools

Use `tools/list` to discover available MCP tools, then follow this loop:

1. Build firmware.
2. Check debugger availability with `debugger_info` if setup is unclear.
3. Probe with `probe_target`.
4. Flash with `flash_firmware` using `image_path`, or call `artifact_upload` first and flash the returned `artifact_id`.
5. For serial feedback, use `com_session_start`, `com_write`, `com_read`, and `com_session_stop`.
6. For CAN, use `can_session_start`, `can_send`, `can_read`, and `can_session_stop`.
7. For simulated sensors, loads, and faults, use the configured adapter tools.
8. Read the tool result and `get_last_report`; diagnose failures with `classify_last_error`.

Do not use raw OpenOCD commands, arbitrary COM-port shell tools, direct CAN adapter tools, or direct test-adapter access when a HardCI MCP tool is available. Treat `permission_denied` as authoritative and stop.

## pytest Suites

For CI regression suites, the installed package registers a pytest plugin. The `hardci` fixture drives the same tools via `hardci.call(name, arguments)`. Tests skip when no `.hardci/config.yaml` exists and fail loudly when the config is invalid. See `examples/pytest/` and `examples/nucleo-f446re_demo/tests/`.
