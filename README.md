# damArea v2.0

Geospatial measurement pipeline for reservoir perimeter, surface area, and timescale tracking using Sentinel-2 satellite imagery.

## Overview

This project provides an automated pipeline to estimate:
- Reservoir surface area
- Area tracking over time (Timeseries analysis)
- Uncertainty quantification (Resolution & Threshold sensitivity)

The system performs:
- Automatic CRS (UTM) handling and coordinate transformations
- NDWI-based water detection with automated cloud masking
- Connected reservoir selection ensuring we analyze the water body physically attached to the queried dam
- Adaptive bounding box expansion and resolution clamping (adhering to Sentinel-Hub API limits)
- Error margin estimations based on spatial and index resolutions
- Autonomous Cloud-Failovers (Radar + VV Thresholding)

## Architecture

The project utilizes a robust, modular pipeline:
- `fetch_dam/`: Geocoding dams (OpenStreetMap fallback) and loading known dam structural coordinates.
- `pipeline/`: Core steps for raw data acquisition, NDWI processing, parsing pixel areas, and plotting visualizations.
- `sentinel/`: Handlers for the Sentinel-Hub API requests, caching, and arrays.
- `tiling/` & `geometry/`: Geographic spatial manipulations and segment intersections.
- `processing/` & `uncertainty/`: Water mask processing sequences, algorithms to capture the largest connected geometries, and sensitivity models to provide standard errors on computed areas.

## Installation

### Prerequisites
- Python 3.8 or higher
- A Sentinel Hub account with API access

### Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/rushatdixit/damArea.git
   cd damArea
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   Create a `.env` file in the root directory with your Sentinel Hub credentials:
   ```env
   SH_CLIENT_ID=your_client_id
   SH_CLIENT_SECRET=your_client_secret
   SH_INSTANCE_ID=your_instance_id
   ```
   *Obtain these credentials from [Sentinel Hub](https://www.sentinel-hub.com/).*

## Usage

To run the pipeline for a specific dam:

```bash
damArea "dam_name"
```

### Example Run

Executing for a major dam like Bhakra Nangal:
```bash
damArea "Bhakra Nangal"
```

**Terminal Output:**
```text
Running pipeline for: Bhakra Nangal

Found dam in database. Skipping openstreetmap query.
24200.0
Adjusted resolution to : 17
Fetching RGB Data...
RGB received | Shape: (2384, 2372, 3)
Getting NDWI bands...
Computing NDWI...
NDWI range: -1.000 to 1.000
Applying water threshold to NDWI...
Found 1295 water components.
Selected reservoir area: 96.1902 km²
Boundary distance to dam: 54.13 meters
Optimal resolution for reservoir AOI: 15
Fetching RGB Data...
RGB received | Shape: (2449, 1817, 3)
...
[Processing Logs]
...
Computing Area over Time for interval ('2023-01-01', '2023-12-31')...
...
[Timeseries Logs]
...
-----------------------------------
Final Area: 96.2440 ± 2.8614 km²
-----------------------------------

Time elapsed: 148.32 seconds
Pipeline complete.
```

## Advanced Execution (CLI)

You can directly control pipeline logic via precise modular flags using the global `damArea` alias:

```bash
damArea "Khadakwasla Dam" --start-date 2023-01-01 --end-date 2023-12-31 --timeseries-step 30 --verbose y
```

### CLI Arguments
- `--area {y,n}`: Estimate Initial Reservoir Baseline Area.
- `--unc {y,n}`: Process and calculate Coarse, Threshold, and Resolution boundary uncertainties.
- `--time {y,n}`: Scans chronological intervals and performs timeline analysis.
- `--sar {y,n}`: Utilize Sentinel-1 cloud-piercing Radar as an automatic fallback on fully clouded optical intervals.
- `--verbose {y,n}`: Dump matrix arrays down into `./deep_debug` for manual validation!
- `--delete-debug y`: Safely obliterate any previously accumulated image plot caches.

## Visualizations & Sample Outputs

The pipeline automatically compiles its analyses and generates visualization graphics for each dam processed. They are dumped to the `outputs/` folder. Below are our exactly three primary diagnostic snapshots:

### 1. Optical Pipeline Diagnostics
Visualizes the extraction process from Raw RGB, NDWI bounding, up to final isolated water-body contour capturing.
![Pipeline Diagnostics](file:///Users/merucoding/damArea/outputs/Pipeline_Overview.png)

### 2. Autonomous Cloud Fallovers via Sentinel-1 SAR
Tracks times the Sentinel-1 SAR triggers when optical satellites are blinded by extreme weather, rendering the literal backscatter of physical water matrices.
![SAR VV Backscatter Filtering](file:///Users/merucoding/damArea/outputs/SAR_VV_Example.png)

### 3. Timeseries Uncertainty Dashboard
Plots systematic evaluation charts measuring scale robustness against varying NDWI thresholds and pixel physical scales alongside chronological tracking.
![Analysis Dashboard](file:///Users/merucoding/damArea/outputs/Analysis_Dashboard.png)

## Mathematical Models

To ensure metric rigor and replicability, the system computes properties via the following mathematical boundaries:

### 1. Normalized Difference Water Index (NDWI)
Water bodies are strictly delineated using NDWI, calculated via the Sentinel-2 Green (B03) and Near-Infrared or NIR (B08) optical bands:

$$ NDWI = \frac{\text{Green} - \text{NIR}}{\text{Green} + \text{NIR}} $$

Pixels observing an $NDWI > \text{threshold}$ (typically tuned around 0.2 - 0.3) are computationally flagged as isolated water representations. 

### 2. Physical Area Integration
Given the UTM geographic projection constraints bounding the coordinates, the active pixel layouts are processed as strictly rectangular arrays. A reservoir's overall surface footprint is an arithmetic integration of water pixels normalized to square kilometers:

$$ \text{Area}_{\text{km}^2} = \frac{\sum (\text{Water Pixels}) \times \text{Resolution}_{\text{meters}}^2}{1,000,000} $$

### 3. Cumulative Uncertainty Extraction
To derive the final operational margin of error, the system isolates the sensitivity margin (or variance trajectory) across dynamic NDWI thresholds ($U_t$) and varying spatial API resolutions ($U_r$). The final combined system error bound ($\pm U_{total}$) is rooted via a sum of squares methodology yielding standard geometric variance estimation:

$$ U_{total} = \sqrt{(U_t)^2 + (U_r)^2} $$

## SAR Architecture and Radar Backscatter Mechanics

**What is SAR (Synthetic Aperture Radar)?**
Sentinel-2 optical satellites cannot pierce heavy cloud cover (e.g., during monsoon seasons), leaving massive timeline data gaps. To overcome this, the pipeline autonomously falls back on **Sentinel-1 SAR** (Synthetic Aperture Radar). SAR emits its own active microwave pulses (C-band) towards the Earth's surface and records the returning echoes (backscatter). Because microwave frequencies operate at much longer wavelengths than visible light, they penetrate clouds, rain, and fog with 100% visibility.

**The Mathematics of SAR Water Extraction:**
Water extraction using SAR operates on the physics of **Specular Reflection**. 
1. When radar pulses hit a flat surface (like a calm reservoir), the energy bounces *away* from the satellite in a V-angle, resulting in effectively zero returning energy (an exceedingly dark pixel or a phenomenally low backscatter coefficient).
2. Conversely, rough terrain (forests, dams, buildings) scatters the pulse in all directions (**Diffuse Scattering**), returning high backscatter to the sensor (resulting in phenomenally bright pixels).

**Our Specific Implementation**:
The pipeline requests the **VV Polarization** (Vertical Send, Vertical Receive) sequence from `.SENTINEL1_IW` (Interferometric Wide Swath) GRD collections. The raw amplitude signal arrays arrive with extreme exponential variance.

1. **Backscatter Thresholding:** By evaluating the coefficient histogram empirically, we isolate everything underneath `SAR_THRESHOLD = 0.05`. Any physical pixel reflecting less than `0.05` intensity energy is computationally verified as fluid water. In extreme noise cases, `normalize_rgb()` percentile bounds stretching ensures outlier pixels don't artificially crush dynamic range!
2. **Connectivity Mapping:** The identical connected-components isolation logic applied to optical NDWI works simultaneously against the SAR logic. Since radar noise is exceedingly prone to speckling (salt and pepper static backscatter), our bounding constraint strictly selects the largest single coalesced body connected near the geographical OpenStreetMap anchor ensuring puddles and static noise don't corrupt metric tracking.
