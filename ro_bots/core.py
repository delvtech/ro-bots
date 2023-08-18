"""Ro-bots."""
from pkg_resources import resource_filename
from ro_bots import run_hyperdrive_agents

def run_bots(trade_list=None):
    """Run ro-bots."""
    run_hyperdrive_agents.main(["--develop"], trade_list=trade_list, abi_folder=f"{resource_filename('ro_bots', 'abis')}")

if __name__ == "__main__":
    run_bots()
