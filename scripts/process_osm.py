"""Turn an Overpass 'raw OSM data' export into one point per public pool.

Usage: python3 -I process_osm.py <export.json> <states.geojson> <rls_2025.csv> <out.csv>
- one point per element (node position, or way/relation centre)
- points within 150 m of each other are merged (an aquatic centre often has
  several pools mapped separately); named sports/aquatic centres are kept first
- each point is assigned to a state by point-in-polygon
"""
import json, csv, math, sys, collections
from shapely.geometry import shape, Point

export, states_path, rls_path, out = sys.argv[1:5]
ABBR = {'New South Wales': 'NSW', 'Victoria': 'VIC', 'Queensland': 'QLD', 'South Australia': 'SA',
        'Western Australia': 'WA', 'Tasmania': 'TAS', 'Northern Territory': 'NT',
        'Australian Capital Territory': 'ACT'}
states = [(f['properties']['STATE_NAME'], shape(f['geometry']))
          for f in json.load(open(states_path))['features']]

pts = []
for e in json.load(open(export))['elements']:
    if e['type'] == 'node':
        lat, lon = e['lat'], e['lon']
    elif 'center' in e:
        lat, lon = e['center']['lat'], e['center']['lon']
    else:
        continue
    t = e.get('tags', {})
    indoor = ('yes' if t.get('covered') == 'yes' or t.get('indoor') == 'yes' or t.get('building')
              else 'no' if t.get('covered') == 'no' else '')
    pts.append(dict(osm_id=f"{e['type'][0]}{e['id']}", name=t.get('name', ''), type=t.get('leisure', ''),
                    lat=lat, lon=lon, indoor=indoor, wheelchair=t.get('wheelchair', ''),
                    operator=t.get('operator', '')))

import re
NATURAL = re.compile(r"rock ?pools?\b|\brocks\b|ocean|tidal|sea ?baths|swimming hole|waterhole|netted|"
                     r"enclosure|swimming at|natural spring|bore baths|artesian|thermal pool|"
                     r"(beach|esplanade|swimming|waterfront) lagoon|^the rock pool$", re.I)
SWIM_SCHOOL = re.compile(r"swim(ming)? school|learn to swim|swim academy|aquatic achievers", re.I)
NOT_PUBLIC = re.compile(r"(?<!state school/public )\b(school|college|grammar)\b|\bSH swimming|hotel|resort|motel|"
                        r"apartment|caravan|holiday park|retirement|hydrotherapy|private|snooker|billiard", re.I)
GENERIC = re.compile(r"^(\d+ ?m(etre)?|lap|leisure|outdoor|indoor|kids?|toddlers?|wading|learn[- ]to[- ]swim|"
                     r"main|program|dive|diving|spa|warm[- ]water|heated)?\s*(swimming )?pools?$|^swimming$|^v - pool$",
                     re.I)


def category(p):
    n = p['name']
    if p['type'] == 'water_park':
        return 'water_park'
    if SWIM_SCHOOL.search(n):
        return 'swim_school'
    if NOT_PUBLIC.search(n) and not re.search(r'public pool', n, re.I):
        return 'not_public'
    if NATURAL.search(n):
        return 'ocean_or_natural'
    if p['type'] == 'sports_centre':
        return 'aquatic_centre'
    return 'public_pool'


for p in pts:
    p['category'] = category(p)
    p['generic'] = (p['name'] == '' or bool(GENERIC.match(p['name'].strip())))

PRIORITY = {'aquatic_centre': 0, 'public_pool': 1, 'swim_school': 1, 'water_park': 2, 'ocean_or_natural': 3, 'not_public': 4}
pts.sort(key=lambda p: (p['generic'], PRIORITY[p['category']], p['name'] == ''))


def dist_m(a, b):
    dy = (a['lat'] - b['lat']) * 111000
    dx = (a['lon'] - b['lon']) * 111000 * math.cos(math.radians(a['lat']))
    return math.hypot(dx, dy)


# grid index so the 150 m merge stays fast
grid, keep = collections.defaultdict(list), []
for p in pts:
    gx, gy = int(p['lon'] / 0.01), int(p['lat'] / 0.01)
    near = [k for dx in (-1, 0, 1) for dy in (-1, 0, 1) for k in grid[(gx + dx, gy + dy)]]
    # generic/unnamed pools are usually one tank inside a bigger complex: merge them more widely
    if any(dist_m(p, k) < (400 if p['generic'] else 150) for k in near):
        continue
    keep.append(p)
    grid[(gx, gy)].append(p)

for p in keep:
    pt = Point(p['lon'], p['lat'])
    s = next((n for n, g in states if g.contains(pt)), None)
    if s is None:  # on the coastline / offshore island: nearest state
        s = min(states, key=lambda x: x[1].distance(pt))[0]
    p['state_abbr'] = ABBR[s]
    p['lat'], p['lon'] = round(p['lat'], 5), round(p['lon'], 5)

print('elements', len(pts), '-> after merging', len(keep))
print(collections.Counter(p['category'] for p in keep))
for cat in ('not_public', 'ocean_or_natural'):
    print(cat, 'examples:', [p['name'] for p in keep if p['category'] == cat][:25])
counted = [p for p in keep if p['category'] in ('aquatic_centre', 'public_pool', 'swim_school')]
print('\nCoverage using aquatic centres + public pools + swim schools:')
c = collections.Counter(p['state_abbr'] for p in counted)
rls = {r['state_abbr']: int(r['total_facilities']) for r in csv.DictReader(open(rls_path))}
for s in rls:
    print(f"{s:4}{c[s]:5} of {rls[s]:4} RLS facilities  {100 * c[s] / rls[s]:5.0f}%")
print('total', len(counted), 'of', sum(rls.values()), f"{100 * len(counted) / sum(rls.values()):.0f}%")

keep = [p for p in keep if p['category'] != 'not_public']
fields = ['osm_id', 'name', 'category', 'lat', 'lon', 'state_abbr', 'indoor', 'wheelchair', 'operator']
for p in keep:
    del p['type'], p['generic']
with open(out, 'w', newline='') as fh:
    w = csv.DictWriter(fh, fieldnames=fields)
    w.writeheader()
    w.writerows(keep)
