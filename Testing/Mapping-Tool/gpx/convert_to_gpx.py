import gpxpy
import gpxpy.gpx
import json
import os
from xml.etree.ElementTree import Element
from datetime import datetime

TRACKER_NAME = "test"

gpx = gpxpy.gpx.GPX()

gpx_track = gpxpy.gpx.GPXTrack()
gpx.tracks.append(gpx_track)

# create GPX segment
gpx_segment = gpxpy.gpx.GPXTrackSegment()
gpx_track.segments.append(gpx_segment)

# load JSON data
with open(f'{TRACKER_NAME}.json', 'r') as f:
    data = json.load(f)

# iterate through each point in the JSON list
for point_dict in data:
    for point_key, point in point_dict.items():
        # convert time string to datetime object
        time = datetime.fromisoformat(point['time'].replace('Z', '+00:00'))

        gpx_point = gpxpy.gpx.GPXTrackPoint(
            time=time,
            latitude=point['lat'],
            longitude=point['long']
        )

        # create extensions for telemetry data
        telemetry_data = Element('TelemetryData')
        for key, value in point['telemetry'].items():
            data_element = Element(key)
            data_element.text = str(value)
            telemetry_data.append(data_element)
        
        # append telemetry data to the point's extensions
        gpx_point.extensions.append(telemetry_data)

        # append the point to the GPX segment
        gpx_segment.points.append(gpx_point)

# write the updated GPX data back to the file
with open(f'{TRACKER_NAME}.gpx', 'w') as f:
    f.write(gpx.to_xml())
