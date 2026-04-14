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

def plot_coarse_uncertainty(coarse_unc):
    resolutions = coarse_unc.coarse_resolutions
    bbox_areas = coarse_unc.bbox_areas_km2
    res_areas = coarse_unc.reservoir_areas_km2
    times = coarse_unc.times_taken

    fig, axes = plt.subplots(1, 3, figsize=(15, 4))

    # BBox Area vs Coarse Resolution
    axes[0].plot(resolutions, bbox_areas, marker="o")
    axes[0].set_xlabel("Coarse Resolution (m)")
    axes[0].set_ylabel("Bounding Box Area (km²)")
    axes[0].set_title("BBox Area vs Coarse Reso")
    axes[0].grid(True)

    # Reservoir Area vs Coarse Resolution
    axes[1].plot(resolutions, res_areas, marker="o", color="orange")
    axes[1].set_xlabel("Coarse Resolution (m)")
    axes[1].set_ylabel("Reservoir Area (km²)")
    axes[1].set_title("Reservoir Area vs Coarse Reso")
    axes[1].grid(True)

    # Time vs Coarse Resolution
    axes[2].plot(resolutions, times, marker="o", color="green")
    axes[2].set_xlabel("Coarse Resolution (m)")
    axes[2].set_ylabel("Time (seconds)")
    axes[2].set_title("Calculation Time vs Coarse Reso")
    axes[2].grid(True)

    plt.tight_layout()
    plt.show()