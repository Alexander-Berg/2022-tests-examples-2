import os
import subprocess
import yatest.common


def test_build():
    cargo = yatest.common.build_path('noc/hbfng/rust_toolchain/.cargo/bin/cargo')
    bin_dir = os.path.dirname(cargo)
    assert os.path.basename(bin_dir), bin_dir
    cargo_home = os.path.dirname(bin_dir)
    os.environ['CARGO_HOME'] = cargo_home
    rustup_home = os.path.join(os.path.dirname(cargo_home), ".rustup")
    os.environ['RUSTUP_HOME'] = rustup_home
    subprocess.run([cargo, "run", "--release", "--", "--help"], check=True)
