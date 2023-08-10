"""Install ro-bots."""
import os
import urllib.request
from setuptools import setup
import shutil
import os

# REPO = "delvtech/elf-simulations"
REPO = "wakamex/elf-simulations"

contract_names = ["ERC20Mintable", "IHyperdrive"]
agent0_scripts = ["run_hyperdrive_agents.py"]
ABI = "https://raw.githubusercontent.com/{repo}/main/packages/hyperdrive/src/abis/{contract}.sol/{contract}.json"
ABI_PATH = "ro_bots/packages/hyperdrive/src/abis/{contract}.sol/{contract}.json"
AGENT0_SRC = "https://raw.githubusercontent.com/{repo}/main/lib/agent0/bin/{script}"
AGENT0_PATH = "ro_bots/{script}"

# download ABIs
for contract_name in contract_names:
    URL = ABI.format(contract=contract_name, repo=REPO)
    TARGET_PATH = ABI_PATH.format(contract=contract_name)
    if not os.path.exists(os.path.dirname(TARGET_PATH)):
        os.makedirs(os.path.dirname(TARGET_PATH))
    urllib.request.urlretrieve(URL, TARGET_PATH)

# download scripts outside of packages
for script in agent0_scripts:
    URL = AGENT0_SRC.format(script=script, repo=REPO)
    TARGET_PATH = AGENT0_PATH.format(script=script)
    if not os.path.exists(os.path.dirname(TARGET_PATH)):
        os.makedirs(os.path.dirname(TARGET_PATH))
    urllib.request.urlretrieve(URL, TARGET_PATH)

setup(
    name='ro-bots',
    version='0.1.0',
    packages=["ro_bots"],
    # other package metadata...
    install_requires=[
        f"elfpy[base] @ git+https://github.com/{REPO}/#subdirectory=lib/elfpy",
        f"agent0[base] @ git+https://github.com/{REPO}/#subdirectory=lib/agent0",
        f"chainsync[base] @ git+https://github.com/{REPO}/#subdirectory=lib/chainsync",
        f"ethpy[base] @ git+https://github.com/{REPO}/#subdirectory=lib/ethpy",
    ]
)

shutil.rmtree('build', ignore_errors=True)
shutil.rmtree('ro_bots.egg-info', ignore_errors=True)
