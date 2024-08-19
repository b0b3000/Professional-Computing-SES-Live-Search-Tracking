import folium
from folium.plugins import TimestampedGeoJson
import os

lines = [
    {
        "coordinates": [
            [116.07863524846368, -31.865184419408514],
            [116.07911971292083, -31.86478329243488],
        ],
        "dates": ["2024-08-18T00:00:00", "2024-08-18T00:10:00"],
        "color": "red",
        "data": "here is some additional data"
    },
    {
        "coordinates": [
            [116.07911971292083, -31.86478329243488], 
            [116.07975560446562, -31.865369779903773]
        ],
        "dates": ["2024-08-18T00:10:00", "2024-08-18T00:20:00"],
        "color": "red",
        "data": "here is some additional data"
    },
    {
        "coordinates": [
            [116.07975560446562, -31.865369779903773], 
            [116.08041136907269, -31.864828128884]
        ],
        "dates": ["2024-08-18T00:20:00", "2024-08-18T00:30:00"],
        "color": "red",
        "data": "here is some additional data"
    },
    {
        "coordinates": [
            [116.08041136907269, -31.864828128884], 
            [116.0804396265383, -31.866904109870646]
        ],
        "dates": ["2024-08-18T00:30:00", "2024-08-18T00:40:00"],
        "color": "red",
        "data": "here is some additional data"
    },
]

features = [
    {
        "type": "Feature",
        "geometry": {
            "type": "LineString",
            "coordinates": line["coordinates"],
        },
        "properties": {
            "times": line["dates"],
            "tooltip": line["data"] + str(line["dates"]),
            "style": {
                "color": line["color"],
                "weight": 5,
            },
        },
    }
    for line in lines
]

current_dir = os.path.dirname(__file__)
path = os.path.join(current_dir, 'footprint.html')      # Find correct location to store map.
m = folium.Map((-31.865184419408514, 116.07863524846368), control_scale=True, zoom_start=17)    # Arbitrary location in John Forrest National Park.

TimestampedGeoJson(
    {
        "type": "FeatureCollection",
        "features": features,
    },
    transition_time=100,
    period="PT1M",
    loop=False,
    add_last_point=True,
).add_to(m)

m.save(path)