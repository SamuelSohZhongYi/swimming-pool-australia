# Data — Public Swimming Pools Across Australia

FIT3179 Data Visualisation 2 · Samuel Soh Zhong Yi (34076808) · collected 13 Oct 2026

## Files ready

| File | What it holds | Used for | Source |
|---|---|---|---|
| `aus_states.topojson` | 8 state/territory boundaries, simplified (21 KB). TopoJSON object name: `states`; state name field: `properties.STATE_NAME` | Base layer for every map | rowanhogan/australian-states (GitHub), derived from ABS boundaries; simplified to 8% with mapshaper |
| `rls_pools_by_state_2024.csv` | Total, public-owned and public-accessible pools per state | Proportional symbol map | Royal Life Saving Society – Australia (2024). *Safer Public Pools Report 2024*. https://www.royallifesaving.com.au/__data/assets/pdf_file/0009/82944/RLS_SaferPP_Report24_v7FINAL.pdf |
| `rls_facilities_visits_by_state_2025.csv` | Facilities by type (outdoor pool / aquatic centre / swim school) and annual visits per state | Visits per person, facility mix | Royal Life Saving Society – Australia (2025). *State of Australian Aquatic Facilities 2025*, p. 9. https://www.royallifesaving.com.au/__data/assets/pdf_file/0011/89498/RLS_StateOfIndustry25_Report.pdf |
| `rls_pool_access_by_state.csv` | People with no pool within a 10- or 20-minute drive, 2021 and projected 2028/2030/2032 | Choropleth (% without access). Added columns: `pct_no_pool_10min_2021` (= no_pool_10min_2021 ÷ population_2021) and `label_lon`/`label_lat` (a point inside each state for map labels) | Same 2025 report, p. 16 |
| `rls_key_figures.csv` | Headline numbers: 421 M visits, average pool built 1968, 500 pools (40%) at end of life, $8 B replacement, $9.1 B annual benefit | Isotype, waffle, value chart | RLS 2022 Infrastructure report, 2025 report, RLS value placemat |
| `abs_population_mar2026.csv` | Estimated resident population per state, 31 Mar 2026 | People per pool, visits per person | ABS (2026). *Australia's population grows 1.4% in March 2026*. https://www.abs.gov.au/media-centre/media-releases/australias-population-grows-14-march-2026 |
| `bom_capital_city_climate.csv` | Monthly mean max/min temperature and rainfall, 8 capitals (long format) | Radial seasonal chart | Bureau of Meteorology, Climate statistics for Australian locations, e.g. https://www.bom.gov.au/climate/averages/tables/cw_066062.shtml (station IDs in file) |

## Checks done
- RLS 2024 table: each row public-owned + public-accessible = total; column totals 1,305 and 814 match the report text.
- RLS 2025 table: facility types add to each state total; national 2,103 facilities and 421,343,494 visits match (off by 1 visit from rounding).
- Access table: state populations sum to 25,360,721 and no-pool-in-10-min to 5,954,195, matching the national row.
- ABS states sum to 27,916.1 k vs 27,921.2 k national; the gap is Other Territories (e.g. Christmas Island).
- BOM: Sydney and Melbourne stations have records ending 2020 and 2014 (long-term averages); the others run to 2026.

## Added 13 Oct 2026 (from your downloads)

| File | What it holds | Used for | Source |
|---|---|---|---|
| `osm_public_pools.csv` | 1,814 locations as points (lat, lon, state, name, indoor, wheelchair) with `category` = aquatic_centre / public_pool / swim_school / water_park / ocean_or_natural. Pools within 150 m merged (400 m for unnamed/generic tanks); school, hotel, resort, hydrotherapy pools and billiard halls removed | Dot map, grid bin map | © OpenStreetMap contributors (ODbL), via Overpass Turbo, query `osm_pools_query_v2.overpassql`, 13 Oct 2026; processed with `scripts/process_osm.py` |
| `brisbane_council_pools.csv` | All 22 Brisbane City Council pools: lat/lon, suburb, disability access and parking, open in winter, heated, indoor, 50 m pool, lifeguards, water play, lessons, public transport, Monday open/close times | Brisbane zoom-in map with filters | Brisbane City Council (2026). *Swimming Pool locations*. https://data.brisbane.qld.gov.au/explore/dataset/swimming-pools — CC BY 4.0, updated 12 Oct 2026 |
| `ausplay_activity_ranks.csv` | Top 10 adult activities and their rank, each financial year 2016–17 to 2024–25, with `series` = phone / online | Bump chart | Australian Sports Commission, AusPlay National Data Tables (one file per year), table "Participation by activity (adults)" |
| `ausplay_age_activity_2025.csv` | Participation rate by age group for the top 10 activities, Jan–Dec 2025 | Heatmap | AusPlay National Data Tables, released 30 Apr 2026 |
| `ausplay_swimming_by_year.csv` | Swimming: rate, number of adult participants, rate by sex and age, every period | Trend line, annotations | AusPlay National Data Tables, all years |

Notes:
- Rates are fractions (0.154 = 15.4%). Use `"format": ".0%"` in Vega-Lite.
- **Never connect phone (≤2022–23) and online (≥2023–24) values with one line.** ASC says they cannot be compared. Draw them as two segments.
- Activity names were harmonised: old "Athletics, track and field (includes jogging and running)" and new "Running/jogging" → "Running/athletics".
- **OSM coverage (v2 query)**: counting aquatic centres + public pools + swim schools gives 1,658 = 79% of RLS's 2,103 facilities. By state: QLD 102%, NSW 84%, NT 79%, ACT 70%, VIC 69%, WA 65%, SA 59%, TAS 56%. Caption the dot map "pools mapped in OpenStreetMap"; state-level maps use RLS counts.
- For the dot/grid maps, filter to the three counted categories; show `ocean_or_natural` (77, mostly NSW ocean rock pools) as an optional extra layer.

- Cross-check: 19 of Brisbane's 22 council pools have an OSM point within 300 m (86%), consistent with the QLD coverage estimate.
- Brisbane hours: `weekday_close` is the last closing time on Monday; `split_session` = yes where the pool closes mid-day (Carole Park).

## All data collected ✔

## Join keys
All state CSVs carry `state` (full name, matching `properties.STATE_NAME` in the TopoJSON) and `state_abbr`.
