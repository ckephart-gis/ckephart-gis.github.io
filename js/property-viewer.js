// Parcel Property Viewer - recreation of the Enfield Parcel Property
// Viewer built in Experience Builder, reimplemented here with Leaflet
// and synthetic parcel attributes for portfolio purposes.

document.addEventListener('DOMContentLoaded', function () {
  var mapEl = document.getElementById('property-viewer');
  if (!mapEl) return;

  var center = [38.885, -75.83]; // Denton, MD area, standing in for the town
  var map = L.map('property-viewer', { scrollWheelZoom: false }).setView(center, 16);

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; OpenStreetMap contributors'
  }).addTo(map);

  var zoningColors = { R1: '#56B4E9', R2: '#005B8E', C1: '#954200', I1: '#565E52' };
  var owners = ['Smith J.', 'Doe J.', 'Reed L.', 'Hall M.', 'Park Trust', 'Lowry K.', 'Nguyen T.', 'Diaz M.'];
  var zones = ['R1', 'R1', 'R2', 'C1', 'R1', 'I1', 'R2', 'R1'];

  var sidebar = document.getElementById('property-sidebar');

  var rows = 4, cols = 5, spacing = 0.0011;
  var idNum = 1;
  var minLat = center[0] - (rows * spacing) / 2;
  var minLng = center[1] - (cols * spacing) / 2;

  for (var r = 0; r < rows; r++) {
    for (var c = 0; c < cols; c++) {
      var lat = minLat + r * spacing;
      var lng = minLng + c * spacing;
      var w = spacing * 0.82;
      var bounds = [
        [lat, lng], [lat, lng + w], [lat + w, lng + w], [lat + w, lng]
      ];

      var i = (r * cols + c) % owners.length;
      var zone = zones[i];
      var acreage = (0.15 + (i * 0.07) % 0.9).toFixed(2);
      var parcelId = '12-034-' + String(idNum).padStart(4, '0');

      var poly = L.polygon(bounds, {
        color: '#1F2A24',
        weight: 1,
        fillColor: zoningColors[zone] || '#56B4E9',
        fillOpacity: 0.45
      }).addTo(map);

      (function (poly, parcelId, owner, zone, acreage) {
        var popupHtml =
          '<div style="font-family:\'IBM Plex Mono\',monospace;font-size:0.8rem;">' +
          '<strong>' + parcelId + '</strong><br>' +
          'Owner: ' + owner + '<br>' +
          'Zoning: ' + zone + '<br>' +
          'Acreage: ' + acreage +
          '</div>';
        poly.bindPopup(popupHtml);

        poly.on('mouseover', function () { poly.setStyle({ fillOpacity: 0.75 }); });
        poly.on('mouseout', function () { poly.setStyle({ fillOpacity: 0.45 }); });

        poly.on('click', function () {
          if (sidebar) {
            sidebar.innerHTML =
              '<div class="sidebar-field"><span>PARCEL ID</span>' + parcelId + '</div>' +
              '<div class="sidebar-field"><span>OWNER</span>' + owner + '</div>' +
              '<div class="sidebar-field"><span>ZONING</span>' + zone + '</div>' +
              '<div class="sidebar-field"><span>ACREAGE</span>' + acreage + '</div>';
          }
        });
      })(poly, parcelId, owners[i], zone, acreage);

      idNum++;
    }
  }

  if (sidebar) {
    sidebar.innerHTML = '<p class="mono" style="font-size:0.8rem;color:var(--slate);">Click a parcel to view its attributes.</p>';
  }
});
