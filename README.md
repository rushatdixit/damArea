# Dam Area Measurement System

Geospatial measurement pipeline for reservoir perimeter, surface area, and future volume estimation using Sentinel-2 imagery.

## Overview

This project estimates:
- Reservoir surface area
- Perimeter
- (Planned) Volume
- (Planned) Uncertainty quantification

The system performs:
- Automatic CRS handling
- NDWI-based water detection
- Connected reservoir selection
- Adaptive resolution management

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
   ```
   SH_CLIENT_ID=your_client_id
   SH_CLIENT_SECRET=your_client_secret
   SH_INSTANCE_ID=your_instance_id
   ```
   Obtain these credentials from [Sentinel Hub](https://www.sentinel-hub.com/).

## Usage

To run the pipeline for a specific dam:

```bash
python main.py "Dam Name"
```

For example:

```bash
python main.py "Khadakwasla Dam"
```

The system will:
1. Fetch dam coordinates from OpenStreetMap
2. Determine the optimal area of interest
3. Acquire Sentinel-2 satellite data
4. Process NDWI and detect water bodies
5. Select the reservoir connected to the dam
6. Calculate surface area and perimeter
7. Generate visualizations of the pipeline

Results include area measurements in km², with uncertainty estimates where available.

## Architecture

pipeline/
- acquisition
- processing
- measurement
- models
- utilities
- visuals

## Roadmap

- [ ] Geometric uncertainty modeling
- [ ] Adaptive tiling uncertainty
- [ ] Monte Carlo threshold uncertainty
- [ ] Volume estimation via DEM integration
- [ ] Smarter acquisition strategy

## Disclaimer

For research and experimental purposes.