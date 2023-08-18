"""Prepare imports and constants."""
# pylint: disable=invalid-name, unused-import
import logging
import os
import time
import json
import warnings
from cycler import Cycler
from decimal import Decimal

import numpy as np
import pandas as pd
from agent0.hyperdrive.create_and_fund_accounts import create_and_fund_user_account
from agent0.hyperdrive.exec import setup_experiment
from agent0.hyperdrive.fund_bots import fund_bots

# from ethpy.base import initialize_web3_with_http_provider
# from ethpy.hyperdrive import fetch_hyperdrive_address_from_url
from chainsync.analysis.calc_fixed_rate import calc_fixed_rate
from chainsync.analysis.calc_ohlcv import calc_ohlcv
from chainsync.analysis.calc_pnl import calc_closeout_pnl, calc_total_returns
from chainsync.base import get_transactions, initialize_session
from chainsync.dashboard import get_combined_data, plot_fixed_rate, plot_ohlcv
from chainsync.hyperdrive import get_pool_config, get_pool_info, get_wallet_deltas
from dotenv import load_dotenv
from ethpy.hyperdrive import get_hyperdrive_config
from matplotlib import pyplot as plt
from matplotlib.ticker import FuncFormatter
from numpy import size
from pkg_resources import resource_filename

from ro_bots.core import run_bots as run
