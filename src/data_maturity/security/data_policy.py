"""Fail-closed network classification and data-minimization policy."""

from __future__ import annotations

import ipaddress
from typing import Literal
from urllib.parse import urlsplit

from data_maturity.config import ProviderConfig, SecurityConfig


class PolicyViolation(RuntimeError):
    """Security violations are fatal and must not become degraded assessments."""


def classification(provider: ProviderConfig) -> Literal["LOCAL", "REMOTE"]:
    if provider.provider == "mock":
        return "LOCAL"
    hostname = urlsplit(provider.base_url or "").hostname or ""
    # Avoid DNS rebinding: only literal loopback IP addresses qualify as local.
    try:
        return "LOCAL" if ipaddress.ip_address(hostname).is_loopback else "REMOTE"
    except ValueError:
        return "REMOTE"


def enforce(provider: ProviderConfig, policy: SecurityConfig, contains_raw: bool = False) -> None:
    remote = classification(provider) == "REMOTE"
    if remote and policy.mode == "local_only":
        raise PolicyViolation(
            "local_only forbids remote inference; use a literal loopback endpoint"
        )
    if remote and not policy.allow_metadata_to_remote_models:
        raise PolicyViolation("Remote metadata transmission is prohibited")
    if remote and contains_raw and not policy.allow_raw_data_to_remote_models:
        raise PolicyViolation("Remote raw-value transmission is prohibited")
    if remote and urlsplit(provider.base_url or "").scheme != "https":
        raise PolicyViolation("Remote inference requires HTTPS")
