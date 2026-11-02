#jo
import platform
import subprocess

#jo
PING_HOST = "8.8.8.8"

#jo
def is_online() -> bool:
    count_flag = "-n" if platform.system() == "Windows" else "-c"
    try:
        result = subprocess.run(
            ["ping", count_flag, "1", PING_HOST],
            capture_output=True,
            timeout=2,
        )
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False
    return result.returncode == 0
