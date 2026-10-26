"""Shared compatibility marker for benchmark records and derived artifacts."""

BENCHMARK_PROTOCOL_VERSION = 2


def require_current_protocol(record, source):
    """Reject records that cannot be compared under the current protocol."""
    version = record.get("benchmark_protocol_version")
    if version != BENCHMARK_PROTOCOL_VERSION:
        raise SystemExit(
            f"{source}: unsupported benchmark protocol {version!r}; "
            f"expected {BENCHMARK_PROTOCOL_VERSION}. Re-run this record under the current protocol."
        )
