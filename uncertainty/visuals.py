import matplotlib.pyplot as plt


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
    import matplotlib.dates as mdates
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.gcf().autofmt_xdate()

    plt.tight_layout()
    plt.show()