// Google Earth Engine template for Sentinel-5P HCHO screening over India.
// Paste into the GEE Code Editor after authentication and adapt dates/exports.

var india = ee.Geometry.Rectangle([68, 6, 98, 38]);
var start = '2024-10-01';
var end = '2024-11-30';

var hcho = ee.ImageCollection('COPERNICUS/S5P/OFFL/L3_HCHO')
  .filterBounds(india)
  .filterDate(start, end)
  .select('tropospheric_HCHO_column_number_density');

var meanHcho = hcho.mean().clip(india);
var p90 = hcho.reduce(ee.Reducer.percentile([90])).clip(india);
var hotspots = meanHcho.gte(p90).selfMask();

Map.centerObject(india, 5);
Map.addLayer(meanHcho, {min: 0, max: 0.0003, palette: ['navy', 'cyan', 'yellow', 'red']}, 'Mean HCHO');
Map.addLayer(hotspots, {palette: ['red']}, 'Candidate HCHO hotspots');

Export.image.toDrive({
  image: meanHcho,
  description: 'india_s5p_hcho_mean',
  region: india,
  scale: 1113.2,
  maxPixels: 1e13
});
