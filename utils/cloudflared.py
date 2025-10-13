import os
import platform
import stat
import urllib.request
import shutil
import subprocess
import time
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
DEFAULT_HOSTNAME = os.getenv("HOSTNAME", "")
PORT = 5432


def _choose_download_url():
    system = platform.system().lower()
    machine = platform.machine().lower()

    if machine in ("x86_64", "amd64"):
        arch = "amd64"
    elif machine in ("aarch64", "arm64"):
        arch = "arm64"
    else:
        arch = "amd64"

    if "windows" in system:
        filename = f"cloudflared-windows-{arch}.exe"
        url = f"https://github.com/cloudflare/cloudflared/releases/latest/download/{filename}"
    else:
        filename = f"cloudflared-linux-{arch}"
        url = f"https://github.com/cloudflare/cloudflared/releases/latest/download/{filename}"

    return url, filename


def install_cloudflared(dest_dir=None) -> Path:
    if dest_dir is None:
        dest_dir = os.path.join(os.getcwd(), "cloudflared_bin")
    dest_path = Path(dest_dir)
    dest_path.mkdir(parents=True, exist_ok=True)

    url, filename = _choose_download_url()
    bin_path = dest_path / filename
    if bin_path.exists() and bin_path.stat().st_size > 0:
        return bin_path

    tmp_file = dest_path / "cloudflared.tmp"

    with urllib.request.urlopen(url) as resp, open(tmp_file, "wb") as f:
        shutil.copyfileobj(resp, f)

    tmp_file.rename(bin_path)
    bin_path.chmod(bin_path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    return bin_path


def start_tunnel(binary_path: Path, hostname=DEFAULT_HOSTNAME, local_port=PORT):
    cmd = [
        str(binary_path),
        "access", "tcp",
        "--hostname", hostname,
        "--url", f"localhost:{local_port}"
    ]
    print(f"Starting cloudflared tunnel")
    proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(3) # Let time to start
    return proc

def install_and_start():
    print("Installing cloudflared...")
    binary = install_cloudflared()
    return start_tunnel(binary)