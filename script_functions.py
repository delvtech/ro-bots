from script_imports import *
from chainsync.analysis import calculate_spot_price

def check_docker(restart=False):
    dockerps = os.popen("docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'").read()
    print(dockerps)
    number_of_running_services = dockerps.count("\n")-1
    if number_of_running_services > 0:
        print(f"Found {number_of_running_services} running services", end="")
        if restart:
            print(", restarting docker...")
            start_time = time.time()
            os.system("cd /code/infra && docker compose down -v")
            os.system("cd /code/infra && docker compose up --pull always -d")
            print(f"Restarted docker in {time.time() - start_time:.2f}s")
        else:
            print(", using them.")

def run_trades(trade_list):
    """Allow running in interactive session."""
    try:
        run(trade_list=trade_list)
    except:
        pass

def get_data(session, config_data) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Get data."""
    txn_data = get_transactions(session)
    pool_info = get_pool_info(session, coerce_float=False)
    combined_data = get_combined_data(txn_data, pool_info)
    _, fixed_rate_y = calc_fixed_rate(combined_data, config_data)
    combined_data["fixed_rate"] = fixed_rate_y
    combined_data["spot_price"] = calculate_spot_price(
        combined_data["share_reserves"],
        combined_data["bond_reserves"],
        config_data["initialSharePrice"],
        config_data["invTimeStretch"],
    )
    combined_data["base_buffer"] = combined_data["longs_outstanding"] / combined_data["share_price"] + config_data["minimumShareReserves"]
    return combined_data, pool_info

def plot_positions(data, ax=None, labelx=True, legend=True):
    """Plot positions."""
    _data, ax1 = _prep_plot(data, ax)
    lines1 = ax1.step(_data.reset_index().blockNumber, _data[["longs_outstanding", "shorts_outstanding"]])
    labels1 = [
        f"longs ({_data.longs_outstanding.min()/Decimal(1e3):,.0f}k-{_data.longs_outstanding.max()/Decimal(1e3):,.0f}k)",
        f"shorts ({_data.shorts_outstanding.min()/Decimal(1e3):,.0f}k-{_data.shorts_outstanding.max()/Decimal(1e3):,.0f}k)",
    ]
    ax1 = _label_graph(ax1, lines1, labels1, "Open positions", "# of bonds", labelx, legend)
    return ax1, lines1, labels1

def plot_reserves(data, include_buffer=False, ax=None, labelx=True, legend=True):
    """Plot positions."""
    _data, ax1 = _prep_plot(data, ax)
    names = ["bond_reserves", "share_reserves"]
    labels1 = [
        f"bonds ({_data.bond_reserves.min()/Decimal(1e3):,.0f}k-{_data.bond_reserves.max()/Decimal(1e3):,.0f}k)",
        f"shares ({_data.share_reserves.min()/Decimal(1e3):,.0f}k-{_data.share_reserves.max()/Decimal(1e3):,.0f}k)",
    ]
    if include_buffer is True:
        names += ["base_buffer"]
        labels1 += [f"base buffer ({_data.base_buffer.min()/Decimal(1e3):,.0f}k-{_data.base_buffer.max()/Decimal(1e3):,.0f}k)"]
    lines1 = ax1.step(_data.reset_index().blockNumber, _data[names])
    ax1 = _label_graph(ax1, lines1, labels1, "Reserves", None, labelx, legend)
    return ax1, lines1, labels1

def plot_rate(data, ax=None, labelx=True, legend=True):
    """Plot positions."""
    _data, ax1 = _prep_plot(data, ax)
    lines1 = ax1.step(_data.reset_index().blockNumber, _data[["fixed_rate"]])
    labels1 = [
        f"fixed rate ({_data.fixed_rate.min():,.1%}-{_data.fixed_rate.max():,.1%})",
        # f"spot price ({_data.spot_price.min():,.2f}-{_data.spot_price.max():,.2f})",
    ]
    ax1 = _label_graph(ax1, lines1, labels1, "Rate", None, labelx, legend)
    return ax1, lines1, labels1

def plot_rate_price(data, ax=None, labelx=True, legend=True):
    """Plot positions."""
    _data, ax1 = _prep_plot(data, ax)
    lines1 = ax1.step(_data.reset_index().blockNumber, _data[["fixed_rate", "spot_price"]])
    labels1 = [
        f"fixed rate ({_data.fixed_rate.min():,.1%}-{_data.fixed_rate.max():,.1%})",
        f"spot price ({_data.spot_price.min():,.2f}-{_data.spot_price.max():,.2f})",
    ]
    ax1 = _label_graph(ax1, lines1, labels1, "Rate and price", None, labelx, legend)
    return ax1, lines1, labels1

def plot_buffers(data, ax=None, labelx=True, legend=True):
    """Plot positions."""
    _data, ax1 = _prep_plot(data, ax)
    lines1 = ax1.step(_data.reset_index().blockNumber, _data[["base_buffer"]])
    labels1 = [
        f"base buffer ({_data.base_buffer.min()/Decimal(1e3):,.0f}k-{_data.base_buffer.max()/Decimal(1e3):,.0f}k)",
        # f"share buffer ({_data.share_buffer.min()/Decimal(1e3):,.0f}k-{_data.share_buffer.max()/Decimal(1e3):,.0f}k)",
    ]
    ax1 = _label_graph(ax1, lines1, labels1, "Buffers", None, labelx, legend)
    return ax1, lines1, labels1

def _prep_plot(data, ax=None):
    if ax is None:
        _, ax1 = plt.subplots(figsize=(6, 3))
    else:
        ax1 = ax
    return data.copy(), ax1

def _label_graph(ax, lines, labels, title, ylabel=None, labelx=True, legend=True):
    ax.set_title(title)
    if labelx:
        ax.set_xlabel("Block number")
    if ylabel:
        ax.set_ylabel(ylabel)
    yticks = ax.get_yticks()
    ylim = ax.get_ylim()
    yticks = yticks[(yticks >= ylim[0]) & (yticks <= ylim[1])]
    yticks = np.insert(yticks, 0, 0)  # add origin on the second axis
    # de-dup
    yticks = np.unique(yticks)
    yticks = np.linspace(yticks[0], yticks[-1], len(yticks))
    ax.set_yticks(yticks)
    if legend:
        ax.legend(lines, labels, loc="best")
    return ax

def plot_secondary(data, name, ax1, lines1, labels1):
    """Plot rate."""
    _data = data.copy()
    ax2 = ax1.twinx()
    prop_cycler = plt.rcParams['axes.prop_cycle']
    assert isinstance(prop_cycler, Cycler)
    default_colors = prop_cycler.by_key()['color']
    number_of_existing_lines = len(ax1.lines)
    ax2.step(_data.reset_index().blockNumber, _data[[name]], color=default_colors[number_of_existing_lines])
    ticks2 = ax2.get_yticks()
    ylim1 = ax1.get_ylim()
    ylim2 = ax2.get_ylim()

    # label the second axis and the title
    is_pct = True if name == "fixed_rate" else False
    brackets = "(" + ("%, " if is_pct else "") + "RHS)"
    clean_name = f"{name.replace('_',' ')} {brackets}"
    labels2 = [clean_name]
    format_string = ',.2' + ('%' if is_pct else 'f')
    format_string = ',.2f'
    formatter = FuncFormatter(lambda x, p: format(x, format_string))
    ax2.yaxis.set_major_formatter(formatter)
    ax1.set_title(ax1.get_title() + f" and {clean_name}")
    
    ticks1 = ax1.get_yticks()  # Get the y-tick locations from ax1
    # remove ticks outside of the range
    tick_range1 = ticks1[-1] - ticks1[0]
    percent_of_range_below_0 = -ylim1[0] / tick_range1
    percent_of_range_above_max_tick = (ylim1[-1] - ticks1[-1]) / tick_range1
    highest_visible_tick = max(ticks2[(ticks2 <= ylim2[-1])])
    safe_to_remove_max_tick = highest_visible_tick * percent_of_range_above_max_tick >= float(_data[name].max())
    ticks2 = ticks2[(ticks2 >= ylim2[0])]
    if safe_to_remove_max_tick:
        ticks2 = ticks2[(ticks2 <= ylim2[-1])]
    # update tick range
    tick_range1 = ticks1[-1] - ticks1[0]
    ticks2 = np.insert(ticks2, 0, 0)  # add origin on the second axis
    # de-dup
    ticks1 = np.unique(ticks1)
    ticks2 = np.unique(ticks2)
    ticks2 = np.linspace(ticks2[0], ticks2[-1], len(ticks1))
    ax2.set_yticks(ticks2)
    tick_range2 = ticks2[-1] - ticks2[0]

    # synchronize ticks
    ylim2 = -percent_of_range_below_0 * tick_range2, ticks2[-1] + percent_of_range_above_max_tick * tick_range2
    ax2.set_ylim(ylim2)
    range1, range2 = ylim1[1] - ylim1[0], ylim2[1] - ylim2[0]

    for line in lines1:
        ydata = [float(y) for y in line.get_ydata()]
        ydata_scaled = (ydata - ylim1[0]) / range1 * range2 + ylim2[0]
        ax2.step(line.get_xdata(), ydata_scaled, color=line.get_color())
    lines2 = ax2.get_lines()

    # Combine legends
    lines = lines1 + lines2
    labels = labels1 + labels2
    ax2.legend(lines, labels, loc="best")

    # color secondary axis
    ax2.tick_params(axis='y', colors=lines2[0].get_color())

    plt.savefig("output.png")

    return ax2, lines2, labels2