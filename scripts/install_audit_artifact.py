"""Check release hashes and install a noneditable wheel or source distribution."""

import hashlib
import os
import subprocess
import sys
from pathlib import Path

root = Path("release-artifacts").resolve()
manifest = {}
for line in (root / "SHA256SUMS.txt").read_text().splitlines():
    sha, name = line.split(maxsplit=1)
    manifest[name.lstrip("*")] = sha
for pattern in ("*.whl", "*.tar.gz"):
    artifact = next(root.glob(pattern))
    assert hashlib.sha256(artifact.read_bytes()).hexdigest() == manifest[artifact.name]
pattern = "*.whl" if os.environ["AUDIT_PACKAGE"] == "wheel" else "*.tar.gz"
artifact = next(root.glob(pattern))
subprocess.run([sys.executable, "-m", "pip", "install", f"{artifact}[dev]"], check=True)
import data_maturity  # noqa: E402

assert data_maturity.__version__ == os.environ.get("AUDIT_RELEASE_TAG", "v0.1.3").removeprefix("v")
assert "site-packages" in str(data_maturity.__file__)
print(f"Installed {artifact.name}: {data_maturity.__file__}")
