"""Ro-bots."""
from pkg_resources import resource_filename
from ro_bots import run_hyperdrive_agents

def run_bots():
    """Run ro-bots."""
    run_hyperdrive_agents.main(["--develop"], abi_folder=f"{resource_filename('ro_bots', 'abis')}")

if __name__ == "__main__":
    run_bots()
