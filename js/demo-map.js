// Synthetic parcel demo - illustrates scale-dependent label suppression.
// Not real parcel data. Swap this for a real open-data feature service
// (e.g. your county's ArcGIS REST parcel layer) when you rebuild this
// project with actual recreated data.

document.addEventListener('DOMContentLoaded', function () {
  var mapEl = document.getElementById('demo-map');
  if (!mapEl) return;

  var center = [38.885, -75.83]; // Denton, MD area
  var map = L.map('demo-map', { scrollWheelZoom: false }).setView(center, 16);

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; OpenStreetMap contributors'
  }).addTo(map);

  // Synthetic parcel grid
  var parcels = [];
  var rows = 6, cols = 6, spacing = 0.0012;
  var id = 1;
  for (var r = 0; r < rows; r++) {
    for (var c = 0; c < cols; c++) {
      var lat = center[0] + r * spacing;
      var lng = center[1] + c * spacing;
      var bounds = [
        [lat, lng],
        [lat, lng + spacing * 0.85],
        [lat + spacing * 0.85, lng + spacing * 0.85],
        [lat + spacing * 0.85, lng]
      ];
      parcels.push({ id: 'P-' + String(id).padStart(3, '0'), bounds: bounds, center: [lat + spacing * 0.42, lng + spacing * 0.42] });
      id++;
    }
  }

  var polygons = [];
  var labels = [];

  parcels.forEach(function (p) {
    var poly = L.polygon(p.bounds, {
      color: '#005B8E',
      weight: 1.5,
      fillColor: '#56B4E9',
      fillOpacity: 0.15
    }).addTo(map);
    polygons.push(poly);

    var label = L.marker(p.center, {
      icon: L.divIcon({
        className: 'parcel-label',
        html: '<span style="font-family:\'IBM Plex Mono\',monospace;font-size:10px;color:#1F2A24;background:rgba(236,231,214,0.85);padding:1px 4px;border:1px solid rgba(31,42,36,0.3);">' + p.id + '</span>',
        iconSize: [50, 16]
      })
    });
    labels.push(label);
  });

  function updateLabels() {
    var zoom = map.getZoom();
    labels.forEach(function (label, i) {
      // Suppress every other label when zoomed out to avoid overlap,
      // mirroring the condo/duplicate suppression logic in the real project.
      var shouldShow = zoom >= 17 || i % 2 === 0;
      var onMap = map.hasLayer(label);
      if (shouldShow && !onMap) {
        label.addTo(map);
      } else if (!shouldShow && onMap) {
        map.removeLayer(label);
      }
    });
  }

  updateLabels();
  map.on('zoomend', updateLabels);
});
