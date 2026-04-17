"""
Sentinel hub uses javascript based evalscript
It tells sentinel hub what to do
This script says:
    - Input bands are B3 = Green, B8 = NIR
    - Outputs 2 bands
    - Evaluates whether a pixel is how much green and how much nir
    - The second evalscript outputs rgb as well
SCL:
  - SCL is the way sentinel hub differentiates pixels containing water, vegetation, snow etc.
  - the most important is that it includes clouds
"""

NDWI_EVALSCRIPT = """
//VERSION=3
function setup() {
  return {
    input: ["B03", "B08", "SCL"],
    output: {
      bands: 3,
      sampleType: "FLOAT32"
    }
  };
}

function evaluatePixel(sample) {
  return [sample.B03, sample.B08, sample.SCL];
}
"""

RGB_EVALSCRIPT = """
//VERSION=3
function setup() {
  return {
    input: ["B04", "B03", "B02"],
    output: { bands: 3 }
  };
}

function evaluatePixel(sample) {
  return [sample.B04, sample.B03, sample.B02];
}
"""

SAR_VV_EVALSCRIPT = """
//VERSION=3
function setup() {
  return {
    input: ["VV"],
    output: { bands: 1, sampleType: "FLOAT32" }
  };
}

function evaluatePixel(sample) {
  // Return backscatter in linear scale (already converted by Sentinel Hub depending on config)
  // Usually we use log-scaling (dB) or linear, linearly scaled is standard FLOAT32 mapping
  return [sample.VV];
}
"""
