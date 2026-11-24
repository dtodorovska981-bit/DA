// Turns the outline of the contiguous United States into horizontal line segments,
// plus the positions of the three host cities, in one shared coordinate space.
import fs from 'fs';
import { merge } from 'topojson-client';
import { geoAlbersUsa } from 'd3-geo';
const us = JSON.parse(fs.readFileSync('node_modules/us-atlas/states-albers-10m.json', 'utf8'));
const skip = new Set(['02', '15', '60', '66', '69', '72', '78']);            // Alaska, Hawaii, territories
const land = merge(us, us.objects.states.geometries.filter(g => !skip.has(g.id)));
const rings = land.coordinates.flat();                                       // MultiPolygon -> rings
let minX = 1e9, maxX = -1e9, minY = 1e9, maxY = -1e9;
for (const r of rings) for (const [x, y] of r) { minX = Math.min(minX, x); maxX = Math.max(maxX, x); minY = Math.min(minY, y); maxY = Math.max(maxY, y); }
const STEP = 7, PAD = 24;
const segs = [];
for (let y = Math.ceil(minY) + 1; y < maxY; y += STEP) {
  const xs = [];
  for (const r of rings) for (let i = 0; i < r.length - 1; i++) {
    const [x1, y1] = r[i], [x2, y2] = r[i + 1];
    if ((y1 <= y && y2 > y) || (y2 <= y && y1 > y)) xs.push(x1 + (y - y1) * (x2 - x1) / (y2 - y1));
  }
  xs.sort((a, b) => a - b);
  for (let i = 0; i + 1 < xs.length; i += 2) if (xs[i + 1] - xs[i] >= 4) segs.push([+(xs[i] - minX + PAD).toFixed(1), +(y - minY + PAD).toFixed(1), +(xs[i + 1] - minX + PAD).toFixed(1)]);
}
const proj = geoAlbersUsa().scale(1300).translate([487.5, 305]);            // the projection us-atlas uses
const cities = [['Miami', -80.1918, 25.7617], ['New York', -74.006, 40.7128], ['San Francisco', -122.4194, 37.7749]].map(([name, lon, lat]) => {
  const [x, y] = proj([lon, lat]); return { name, x: +(x - minX + PAD).toFixed(1), y: +(y - minY + PAD).toFixed(1) };
});
const out = { width: Math.ceil(maxX - minX + PAD * 2), height: Math.ceil(maxY - minY + PAD * 2), step: STEP, segments: segs, cities,
  source: 'us-atlas (US Census Bureau cartographic boundaries), Albers USA projection' };
fs.writeFileSync('/home/user/DA/epl-group-build/data/us-lines.json', JSON.stringify(out));
console.log(out.width, 'x', out.height, '| lines', new Set(segs.map(s => s[1])).size, '| segments', segs.length, '| cities', JSON.stringify(cities), '| bytes', JSON.stringify(out).length);
