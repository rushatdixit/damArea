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