/*
  Public swimming pools and aquatic centres in Australia (OpenStreetMap)
  Paste into https://overpass-turbo.eu, click Run, then Export -> "raw OSM data" (JSON).
  "out center" returns one point per pool, so the file stays small.
*/
[out:json][timeout:300];
area["ISO3166-1"="AU"][admin_level=2]->.au;
(
  nwr["leisure"="sports_centre"]["sport"~"swimming"](area.au);
  nwr["leisure"="swimming_pool"]["access"~"^(yes|public|permissive)$"](area.au);
  nwr["leisure"="water_park"](area.au);
);
out center tags;
