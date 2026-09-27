import subprocess
import sys
from pathlib import Path


def test_smoke_script_exits_zero() -> None:
    root = Path(__file__).resolve().parent.parent
    script = root / "scripts" / "smoke_test.py"
    result = subprocess.run(
        [sys.executable, str(script)],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr + result.stdout
