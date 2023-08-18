from script_functions import *

logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("web3").setLevel(logging.WARNING)
logging.getLogger("asyncio").setLevel(logging.WARNING)
logging.getLogger('PIL').setLevel(logging.WARNING)
logging.getLogger('matplotlib').setLevel(logging.WARNING)
warnings.filterwarnings("ignore", category=UserWarning, module="web3.contract.base_contract")

START_BLOCK = 0
LOOKBACK_BLOCK_LIMIT = 100_000  # Look back limit for backfilling
SLEEP_AMOUNT = 1
MAX_LIVE_BLOCKS = 14400

load_dotenv()  # Get postgres env variables if exists

# %%
# setup
contracts_url = "http://localhost:8080/addresses.json"
ethereum_node = "http://localhost:8546"
abi_dir = "./packages/hyperdrive/src/"
session = initialize_session()  # initialize the postgres session
config_params = {"abi_folder": f"{resource_filename('ro_bots', 'abis')}"}
user_account = create_and_fund_user_account(**config_params)
fund_bots(**config_params)  # uses env variables created above as inputs
web3, base_token_contract, hyperdrive_contract, env_config, agent_accounts = setup_experiment(**config_params)
config_data = get_pool_config(session, coerce_float=False)
config_data["invTimeStretch"] = config_data["invTimeStretch"] / 10**18
config_data = config_data.iloc[0]