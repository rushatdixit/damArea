"""
Sentinel Hub evalscripts for requesting specific band combinations.
"""

NDWI_EVALSCRIPT: str = """
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

RGB_EVALSCRIPT: str = """
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

SAR_VV_EVALSCRIPT: str = """
//VERSION=3
function setup() {
  return {
    input: ["VV"],
    output: { bands: 1, sampleType: "FLOAT32" }
  };
}

function evaluatePixel(sample) {
  return [sample.VV];
}
"""
