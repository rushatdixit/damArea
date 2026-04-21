import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np

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

    fig, axes = plt.subplots(2, 3, figsize=(16, 10))
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

    # 4. Timeseries (Cartesian)
    if timeseries_data is not None:
        ts = timeseries_data
        if not ts.times:
            axes[3].text(0.5, 0.5, "No Timeseries Data", ha='center', va='center')
            axes[3].axis('off')
            axes[4].axis('off')
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

            # 5. Timeseries (Polar)
            pos = axes[4].get_position()
            axes[4].remove()
            axes[4] = fig.add_axes(pos, projection='polar')

            angles = [t.timetuple().tm_yday / 365.25 * 2 * np.pi for t in ts.times]
            axes[4].plot(angles, ts.areas_km2, marker="o", linestyle="-", color="b")

            if ts.mean_km2 > 0:
                axes[4].axhline(ts.mean_km2, linestyle="--", color="r", label="Mean Area")
                axes[4].legend(loc='lower left', bbox_to_anchor=(1, 0))
            axes[4].set_title("Area vs Time (Cyclic Year)")

            import calendar
            axes[4].set_xticks(np.linspace(0, 2*np.pi, 12, endpoint=False))
            axes[4].set_xticklabels(calendar.month_abbr[1:13])
    else:
        axes[3].axis('off')
        axes[4].axis('off')

    # 6. Empty
    axes[5].axis('off')

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    import os
    os.makedirs('your_outputs', exist_ok=True)
    plt.savefig('your_outputs/Analysis_Dashboard.png', bbox_inches='tight')
    plt.show()


def show_extrema_dashboard(min_extrema, max_extrema, dam_name=""):
    """
    Shows a dedicated 2x6 extrema dashboard in a separate matplotlib window.
    Each row displays: RGB, NDWI, Optical Mask, Optical Reservoir, SAR Backscatter, SAR Reservoir.
    Row 1 = Global Minimum area date, Row 2 = Global Maximum area date.
    """
    from pipeline.visuals import normalize_rgb

    fig, axes = plt.subplots(2, 6, figsize=(24, 8))

    title = "Extrema Dashboard"
    if dam_name:
        title += f" for {dam_name}"
    fig.suptitle(title, fontsize=16)

    labels = ["RGB", "NDWI", "Optical Mask", "Selected Reservoir", "SAR Backscatter", "SAR Reservoir"]

    for row_idx, (extrema, row_label) in enumerate([(min_extrema, "Min"), (max_extrema, "Max")]):
        data_list = [
            extrema.rgb,
            extrema.ndwi,
            extrema.opt_mask,
            extrema.opt_sel,
            extrema.sar,
            extrema.sar_sel,
        ]
        cmaps = [None, "RdBu", "Blues", "Blues", "gray", "Blues"]

        for col_idx, (data, cmap, label) in enumerate(zip(data_list, cmaps, labels)):
            ax = axes[row_idx][col_idx]
            if data is not None:
                display = data
                if col_idx == 0:
                    display = normalize_rgb(np.array(display))
                elif col_idx == 4:
                    display = normalize_rgb(np.array(display))
                ax.imshow(display, cmap=cmap)
            else:
                ax.text(0.5, 0.5, "N/A", ha='center', va='center', fontsize=14)
            if row_idx == 0:
                ax.set_title(label)
            ax.axis('off')

        axes[row_idx][0].set_ylabel(
            f"Global {row_label}\n({extrema.date_str})",
            fontsize=11, rotation=0, labelpad=80, va='center'
        )

    plt.tight_layout(rect=[0.06, 0.03, 1, 0.93])
    import os
    os.makedirs('your_outputs', exist_ok=True)
    plt.savefig('your_outputs/Extrema_Dashboard.png', bbox_inches='tight')
    plt.show()