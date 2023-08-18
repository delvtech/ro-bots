"""Script to query bot experiment data."""
# pylint: disable=invalid-name
# %%
from script_imports import *

logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("web3").setLevel(logging.WARNING)
logging.getLogger("asyncio").setLevel(logging.WARNING)
logging.getLogger('matplotlib').setLevel(logging.WARNING)
warnings.filterwarnings("ignore", category=UserWarning, module="web3.contract.base_contract")

START_BLOCK = 0
LOOKBACK_BLOCK_LIMIT = 100_000  # Look back limit for backfilling
SLEEP_AMOUNT = 1
MAX_LIVE_BLOCKS = 14400

load_dotenv()  # Get postgres env variables if exists

# %%
# experiment parameters
contracts_url = "http://localhost:8080/addresses.json"
ethereum_node = "http://localhost:8546"
abi_dir = "./packages/hyperdrive/src/"

# %%
# initialization
session = initialize_session()  # initialize the postgres session
# web3 = initialize_web3_with_http_provider(
#     ethereum_node=ethereum_node,
#     request_kwargs={"timeout": 60},
# )
# addresses = fetch_hyperdrive_address_from_url(contracts_url)
# print(f"{addresses=}")
config_params = {
    "abi_folder": f"{resource_filename('ro_bots', 'abis')}",
}
user_account = create_and_fund_user_account(**config_params)
fund_bots(**config_params)  # uses env variables created above as inputs
web3, base_token_contract, hyperdrive_contract, env_config, agent_accounts = setup_experiment(**config_params)

# %%
# config
print(''.join(['=']*23) + "=== Pool Config ===" + ''.join(['=']*23))
pool_config_dict = get_hyperdrive_config(hyperdrive_contract)
for k, v in pool_config_dict.items():
    print(f"{k:20} | {v}")
# %%
# data
txn_data = get_transactions(session, -MAX_LIVE_BLOCKS)
# display(txn_data)

# %%
# pool info
pool_info = get_pool_info(session, -MAX_LIVE_BLOCKS, coerce_float=False)
# display(pool_info)

# %%
# pool config
config_data = get_pool_config(session, coerce_float=False)
config_data["invTimeStretch"] = config_data["invTimeStretch"] / 10**18
config_data = config_data.iloc[0]

# %%
combined_data = get_combined_data(txn_data, pool_info)
wallet_deltas = get_wallet_deltas(session, coerce_float=False)

(fixed_rate_x, fixed_rate_y) = calc_fixed_rate(combined_data, config_data)
ohlcv = calc_ohlcv(combined_data, config_data, freq="5T")

start_time = time.time()
current_returns, current_wallet = calc_total_returns(config_data, pool_info, wallet_deltas)
current_wallet = calc_closeout_pnl(current_wallet, pool_info, env_config)  # calc pnl using closeout method
current_wallet.delta = current_wallet.delta.astype(float)
current_wallet.pnl = current_wallet.pnl.astype(float)
current_wallet.closeout_pnl = current_wallet.closeout_pnl.astype(float)
print(f"calculated PNL in {time.time() - start_time=}")

# %%
plt.step(combined_data.reset_index().blockNumber, combined_data[["longs_outstanding","shorts_outstanding"]])
plt.legend(["longs", "shorts"])

# %%
# ohlcv
# fig = plt.figure(figsize=(8, 4))
# ax_ohlcv = fig.add_subplot(1, 2, 1)
# ax_vol = fig.add_subplot(1, 2, 2)
# plot_ohlcv(ohlcv, ax_ohlcv, ax_vol)

# %%
