import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def plot_threshold_uncertainty(threshold_unc):
    thresholds = threshold_unc.thresholds
    areas = threshold_unc.areas_km2

    plt.figure(figsize=(6,4))

    plt.plot(thresholds, areas, marker="o")
    plt.axhline(threshold_unc.mean_km2, linestyle="--")
    plt.xlabel("NDWI Threshold")
    plt.ylabel("Area (km²)")
    plt.title("Threshold Sensitivity")
    plt.grid(True)

    plt.tight_layout()
    plt.show()

def plot_resolution_uncertainty(resolution_unc):
    resolutions = resolution_unc.resolutions
    areas = resolution_unc.areas_km2

    plt.figure(figsize=(6,4))

    plt.plot(resolutions, areas, marker="o")
    plt.axhline(resolution_unc.mean_km2, linestyle="--")
    plt.xlabel("Resolution (m)")
    plt.ylabel("Area (km²)")
    plt.title("Resolution Sensitivity")
    plt.grid(True)

    plt.tight_layout()
    plt.show()

def plot_uncertainties(threshold_unc, resolution_unc):
    fig, axes = plt.subplots(1,2, figsize=(12,4))

    # Threshold
    axes[0].plot(threshold_unc.thresholds, threshold_unc.areas_km2, marker="o")
    axes[0].set_xlabel("NDWI Threshold")
    axes[0].set_ylabel("Area (km²)")
    axes[0].set_title("Threshold Sensitivity")
    axes[0].grid(True)

    # Resolution
    axes[1].plot(resolution_unc.resolutions, resolution_unc.areas_km2, marker="o")
    axes[1].set_xlabel("Resolution (m)")
    axes[1].set_ylabel("Area (km²)")
    axes[1].set_title("Resolution Sensitivity")
    axes[1].grid(True)

    plt.tight_layout()
    plt.show()

def plot_timeseries(timeseries, dam_name: str = ""):
    times = timeseries.times
    areas = timeseries.areas_km2

    if not times or not areas:
        print("No timeseries data to plot.")
        return

    plt.figure(figsize=(8,4))

    plt.plot(times, areas, marker="o", linestyle="-", color="b")
    if timeseries.mean_km2 > 0:
        plt.axhline(timeseries.mean_km2, linestyle="--", color="r", label="Mean Area")

    plt.xlabel("Date")
    plt.ylabel("Area (km²)")
    title = f"Area vs Time"
    if dam_name:
        title += f" for {dam_name}"
    plt.title(title)
    plt.grid(True)
    if timeseries.mean_km2 > 0:
        plt.legend()
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.gcf().autofmt_xdate()

    plt.tight_layout()
    plt.show()

def plot_coarse_uncertainty(coarse_unc):
    resolutions = coarse_unc.coarse_resolutions
    times = coarse_unc.times_taken

    plt.figure(figsize=(6, 4))
    plt.plot(resolutions, times, marker="o", color="green")
    plt.xlabel("Coarse Resolution (m)")
    plt.ylabel("Time (seconds)")
    plt.title("Calculation Time vs Coarse Reso")
    plt.grid(True)

    plt.tight_layout()
    plt.show()

def show_analysis_overview(unc_res=None, timeseries_data=None, dam_name=""):
    """
    Shows all uncertainty and timeseries analyses in a single dashboard popup.
    Supports rendering a subset of panels if either parameter is None.
    """
    if unc_res is None and timeseries_data is None:
        print("No analysis data to plot.")
        return

    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    axes = axes.flatten()

    if dam_name:
        fig.suptitle(f"Analysis Dashboard for {dam_name}", fontsize=16)
    else:
        fig.suptitle("Analysis Dashboard", fontsize=16)

    # 1. Threshold
    if unc_res is not None:
        th = unc_res.threshold_unc
        axes[0].plot(th.thresholds, th.areas_km2, marker="o")
        axes[0].axhline(th.mean_km2, linestyle="--")
        axes[0].set_title("Threshold Sensitivity")
        axes[0].set_xlabel("NDWI Threshold")
        axes[0].set_ylabel("Area (km²)")
        axes[0].grid(True)
    else:
        axes[0].axis('off')

    # 2. Resolution
    if unc_res is not None:
        res = unc_res.resolution_unc
        axes[1].plot(res.resolutions, res.areas_km2, marker="o")
        axes[1].axhline(res.mean_km2, linestyle="--")
        axes[1].set_title("Resolution Sensitivity")
        axes[1].set_xlabel("Resolution (m)")
        axes[1].set_ylabel("Area (km²)")
        axes[1].grid(True)
    else:
        axes[1].axis('off')

    # 3. Coarse Time vs Res
    if unc_res is not None:
        co = unc_res.coarse_unc
        axes[2].plot(co.coarse_resolutions, co.times_taken, marker="o", color="green")
        axes[2].set_title("Calculation Time vs Coarse Res")
        axes[2].set_xlabel("Coarse Resolution (m)")
        axes[2].set_ylabel("Time (seconds)")
        axes[2].grid(True)
    else:
        axes[2].axis('off')

    # 4. Timeseries
    if timeseries_data is not None:
        ts = timeseries_data
        if not ts.times:
            axes[3].text(0.5, 0.5, "No Timeseries Data", ha='center', va='center')
            axes[3].axis('off')
        else:
            axes[3].plot(ts.times, ts.areas_km2, marker="o", linestyle="-", color="b")
            if ts.mean_km2 > 0:
                axes[3].axhline(ts.mean_km2, linestyle="--", color="r", label="Mean")
                axes[3].legend()
            axes[3].set_title("Area vs Time")
            axes[3].set_xlabel("Date")
            axes[3].set_ylabel("Area (km²)")
            axes[3].grid(True)
            axes[3].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
            for label in axes[3].get_xticklabels():
                label.set_rotation(45)
                label.set_ha('right')
    else:
        axes[3].axis('off')

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    import os
    os.makedirs('outputs', exist_ok=True)
    plt.savefig('outputs/Analysis_Dashboard.png', bbox_inches='tight')
    plt.show()