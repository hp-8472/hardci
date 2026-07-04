from __future__ import annotations

import json
import sys
import time
from typing import BinaryIO, TextIO

from hardci.comports import ComPortService
from hardci.types import HardCIConfig, JsonObject


def run_com_stdio(
    config: HardCIConfig,
    port_id: str,
    input_stream: BinaryIO | None = None,
    output_stream: TextIO | None = None,
    error_stream: TextIO | None = None,
    max_read_bytes: int | None = None,
    read_wait_timeout_s: float = 0.05,
    eof_idle_timeout_s: float = 0.5,
) -> int:
    input_stream = input_stream or sys.stdin.buffer
    output_stream = output_stream or sys.stdout
    error_stream = error_stream or sys.stderr
    service = ComPortService(config)
    started_ok = False
    failed = False
    try:
        started = service.session_start(port_id, True)
        if not started.get("ok"):
            write_error(error_stream, started)
            return 1
        started_ok = True
        port = config.com_ports[port_id]
        read_size = max_read_bytes or port.max_buffer_bytes
        last_data_at = time.monotonic()
        input_stream_closed = False
        while not failed:
            chunk = input_stream.read1(4096) if hasattr(input_stream, "read1") else input_stream.read(4096)
            if chunk:
                written = service.write_bytes(port_id, chunk, "hardci_com_stdio_write")
                if not written.get("ok"):
                    failed = True
                    write_error(error_stream, written)
            else:
                input_stream_closed = True
            result = service.read_bytes(port_id, read_size, read_wait_timeout_s, "hardci_com_stdio_read")
            if not result.get("ok"):
                failed = True
                write_error(error_stream, result)
                break
            if int(result.get("bytes_read", 0)) > 0:
                output_stream.write(str(result["data"].get("text", "")))
                output_stream.flush()
                last_data_at = time.monotonic()
                continue
            if input_stream_closed and time.monotonic() - last_data_at >= eof_idle_timeout_s:
                break
            time.sleep(0.01)
        return 1 if failed else 0
    finally:
        if started_ok:
            service.session_stop(port_id)
        service.close()


def write_error(output: TextIO, result: JsonObject) -> None:
    output.write(json.dumps(result) + "\n")
    output.flush()
