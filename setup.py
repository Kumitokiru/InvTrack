
# setup.py for InvTrack (Tkinter + matplotlib)

import sys, os
from cx_Freeze import setup, Executable
from matplotlib import get_data_path

# ─── 1) Locate matplotlib data folder ───
mpl_data_dir = get_data_path()

# ─── 2) Build options ────────────────────
build_exe_options = {
    "includes": ["traceback"],     # your module + stdlib traceback
    "packages": ["matplotlib", "tkinter"],   # matplotlib + builtin tkinter
    "excludes": [
        "email", "http", "xml", "unittest",
        "pandas", "pandas._libs",
        # prune unused backends (only QtAgg used by TkAgg)
        "matplotlib.backends.backend_pdf",
        "matplotlib.backends.backend_ps",
        "matplotlib.backends.backend_svg",
        "matplotlib.backends.backend_tkagg"   # not used in pure Tk script
    ],
    "include_files": [
        (mpl_data_dir, "mpl-data"),          # fonts & styles
    ],
    "zip_include_packages": ["*"],
    "zip_exclude_packages": [],
}

# ─── 3) Suppress console on Windows ──────
base = "Win32GUI" if sys.platform == "win32" else None

# ─── 4) Setup call ──────────────────────
setup(
    name="InvTrack",
    version="1.0",
    description="Inventory Restocking Simulator (Tkinter + matplotlib)",
    options={"build_exe": build_exe_options},
    executables=[Executable("main.py", base=base,
                            target_name="InvTrack.exe")],
)

# setup.py for InvTrack (Tkinter + matplotlib)

import sys, os
from cx_Freeze import setup, Executable
from matplotlib import get_data_path

# ─── 1) Locate matplotlib data folder ───
mpl_data_dir = get_data_path()

# ─── 2) Build options ────────────────────
build_exe_options = {
    "includes": ["traceback"],     # your module + stdlib traceback
    "packages": ["matplotlib", "tkinter"],   # matplotlib + builtin tkinter
    "excludes": [
        "email", "http", "xml", "unittest",
        "pandas", "pandas._libs",
        # prune unused backends (only QtAgg used by TkAgg)
        "matplotlib.backends.backend_pdf",
        "matplotlib.backends.backend_ps",
        "matplotlib.backends.backend_svg",
        "matplotlib.backends.backend_tkagg"   # not used in pure Tk script
    ],
    "include_files": [
        (mpl_data_dir, "mpl-data"),          # fonts & styles
    ],
    "zip_include_packages": ["*"],
    "zip_exclude_packages": [],
}

# ─── 3) Suppress console on Windows ──────
base = "Win32GUI" if sys.platform == "win32" else None

# ─── 4) Setup call ──────────────────────
setup(
    name="InvTrack",
    version="1.0",
    description="Inventory Restocking Simulator (Tkinter + matplotlib)",
    options={"build_exe": build_exe_options},
    executables=[Executable("main.py", base=base,
                            target_name="InvTrack.exe")],
)

