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


def _choose_download_url() -> str:
    machine = platform.machine().lower()
    if machine in ("x86_64", "amd64"):
        return "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64"
    if machine in ("aarch64", "arm64"):
        return "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64"
    return "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64"


def install_cloudflared(dest_dir=None) -> Path:
    if dest_dir is None:
        dest_dir = os.path.join(os.getcwd(), "cloudflared_bin")
    dest_path = Path(dest_dir)
    dest_path.mkdir(parents=True, exist_ok=True)

    bin_path = dest_path / "cloudflared"
    if bin_path.exists() and bin_path.stat().st_size > 0:
        return bin_path

    url = _choose_download_url()
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
        "--url", f"localhost:{PORT}"
    ]
    print(f"Démarrage du tunnel Cloudflare vers {hostname}...")
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    time.sleep(3) # Let time to start
    return proc