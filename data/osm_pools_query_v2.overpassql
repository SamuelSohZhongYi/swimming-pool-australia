/*
  v2: public swimming pools and aquatic centres in Australia (OpenStreetMap)
  Adds named pools that have no "access" tag (common for council pools),
  while still leaving out private and backyard pools.
  Paste into https://overpass-turbo.eu -> Run -> Export -> raw OSM data.
*/
[out:json][timeout:300];
area["ISO3166-1"="AU"][admin_level=2]->.au;
(
  nwr["leisure"="sports_centre"]["sport"~"swimming"](area.au);
  nwr["leisure"="sports_centre"]["name"~"aquatic|swim|pool|baths",i](area.au);
  nwr["leisure"="swimming_pool"]["access"~"^(yes|public|permissive|customers)$"](area.au);
  nwr["leisure"="swimming_pool"]["name"~"aquatic|swim|pool|baths|memorial|leisure",i]["access"!~"^(private|no)$"](area.au);
  nwr["leisure"="water_park"](area.au);
);
out center tags;
