from __future__ import annotations

import json
import sys
from typing import TextIO

from hardci.config import ConfigError, load_config
from hardci.mcp import handle_mcp_message, parse_error_response
from hardci.tools import HardCIToolService
from hardci.types import HardCIConfig


def run_stdio_server(config: HardCIConfig, input_stream: TextIO | None = None, output_stream: TextIO | None = None) -> int:
    input_stream = input_stream or sys.stdin
    output_stream = output_stream or sys.stdout
    tools = HardCIToolService(config)
    try:
        for raw_line in input_stream:
            line = raw_line.strip()
            if not line:
                continue
            try:
                message = json.loads(line)
            except json.JSONDecodeError:
                write_message(output_stream, parse_error_response())
                continue
            response = handle_mcp_message(message, tools)
            if response is not None:
                write_message(output_stream, response)
    finally:
        tools.close()
    return 0


def mcp_stdio(config_path: str | None = None) -> int:
    try:
        return run_stdio_server(load_config(config_path))
    except ConfigError as error:
        sys.stderr.write(json.dumps(error.to_dict(), indent=2) + "\n")
        return 2


def write_message(output_stream: TextIO, message: object) -> None:
    output_stream.write(json.dumps(message) + "\n")
    output_stream.flush()
