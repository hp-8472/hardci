# HardCI

**HardCI gives AI coding agents safe, project-scoped access to real embedded hardware.**

HardCI is a Python/PyPI package that exposes bounded MCP tools for probing, flashing, resetting, artifact validation, serial feedback, CAN stimuli, reports, and logs without giving an agent arbitrary host or debugger access.

## Install

Recommended user install:

```bash
pipx install hardci
hardci init
hardci doctor
```

Without pipx:

```bash
python -m pip install --user hardci
python -m hardci init
python -m hardci doctor
```

## MCP Entry

Project-local `.mcp.json`:

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

## Common Commands

```text
hardci init
hardci doctor
hardci com-ports
hardci mcp-stdio --config .hardci/config.yaml
hardci com-stdio --config .hardci/config.yaml --port dut_uart
hardci schema --output hardci-config.schema.json
hardci skill-install --agent opencode
```

## Development

```bash
python -m pip install -e '.[dev]'
pytest
python -m build
twine check dist/*
```

The package is configured for PyPI publishing through GitHub trusted publishing in `.github/workflows/pypi-publish.yml`.

## License

Apache-2.0
