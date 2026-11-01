# Source this file in bash or zsh before setup, tests, or rendering on the Mini.
# Keep the host-specific environment outside the teaching Python 3.11 setup.
_dx_volume='/Volumes/LOCKE STATION'
_dx_uuid="$(/usr/bin/python3 - <<'PY'
import plistlib
import subprocess
data = plistlib.loads(subprocess.check_output([
    '/usr/sbin/diskutil', 'info', '-plist', '/Volumes/LOCKE STATION']))
if data.get('MountPoint') != '/Volumes/LOCKE STATION':
    raise SystemExit('LOCKE STATION is not mounted at the expected path')
print(data.get('VolumeUUID', ''))
PY
)"
if [ "$_dx_uuid" != '4F16BA40-1497-4E5E-A6E8-4B8AEEAF4B44' ]; then
    echo 'Diagnostic animation setup stopped: LOCKE STATION identity changed.' >&2
    return 1 2>/dev/null || exit 1
fi
export DX_MINI_ROOT="$_dx_volume/diagnostic-reasoning"
export DX_MINI_REPO="$DX_MINI_ROOT/notebooks_dx_reasoning"
export UV_CACHE_DIR="$DX_MINI_ROOT/cache/uv"
export UV_PYTHON_INSTALL_DIR="$DX_MINI_ROOT/runtime/python"
export UV_PROJECT_ENVIRONMENT="$DX_MINI_REPO/animations/.venv"
export XDG_CACHE_HOME="$DX_MINI_ROOT/cache"
export MPLCONFIGDIR="$DX_MINI_ROOT/cache/matplotlib"
export TMPDIR="$DX_MINI_ROOT/tmp/"
export PATH="$UV_PROJECT_ENVIRONMENT/bin:/Users/reblocke/.local/bin:/opt/homebrew/bin:$PATH"
mkdir -p "$UV_CACHE_DIR" "$UV_PYTHON_INSTALL_DIR" "$MPLCONFIGDIR" "$TMPDIR"
unset _dx_volume _dx_uuid
