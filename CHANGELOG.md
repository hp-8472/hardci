# Changelog

All notable changes to HardCI will be documented in this file.

The format is based on Keep a Changelog, and this project follows Semantic Versioning while pre-1.0 changes may still move quickly.

## [Unreleased]

## [0.1.0] - 2026-07-05

First public release on PyPI.

### Added

- MCP stdio server exposing 35 bounded tools for probing, flashing, resetting, artifact validation, serial and CAN stimuli/feedback, structured reports, and error classification, gated by a project-local `.hardci/config.yaml` policy.
- OpenOCD and STM32CubeProgrammer CLI (`stlink`) debugger backends with success-marker confirmation, structured error classification, and per-action logs.
- Test-adapter layer for sensor/actuator/fault simulation: an `adapters:` config section with channel and fault allowlists enforced before anything reaches the adapter, seven `hardci_adapter_*` MCP tools, a JSON-over-stdio bridge protocol for physical adapters and simulators, and a bundled NTC simulator (`examples/adapters/sim_ntc_adapter.py`).
- pytest plugin: installing `hardci` registers the session-scoped `hardci` fixture that drives the same policy-gated tools in CI regression suites, with per-test stimulus-session cleanup, rootdir-anchored config resolution, and skip-when-absent / fail-when-invalid config semantics.
- CLI commands: `init`, `doctor`, `com-ports`, `mcp-stdio`, `com-stdio`, `schema`, `mcp-config`, and `skill-install` for opencode, Claude Code, and Codex.
- Agent-first, no-admin installation flow: `AI_AGENT_QUICKSTART.md`, `llms.txt`, and `TROUBLESHOOTING.md`, built around `uvx hardci` / `pipx run hardci` with a repository-URL fallback.
- Nucleo-F446RE demo firmware (`examples/nucleo-f446re_demo/`) exercising the complete loop on real hardware: build → flash → reset → assert on the UART boot banner.
- PyPI trusted publishing with a release-tag/package-version guard and digital attestations; CI matrix across Linux/macOS/Windows and Python 3.10–3.13 with ruff linting.
