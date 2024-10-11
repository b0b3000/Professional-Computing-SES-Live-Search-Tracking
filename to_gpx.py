"""This module translates GPX data into JSON data."""

from datetime import datetime
from xml.etree.ElementTree import Element
import gpxpy
import gpxpy.gpx


def convert_json_to_gpx_string(json_data):
    """Translates GPX data into JSON data.

    Args:
        json_data (dict): A dictionary of blob names paired with GeoJSON data.

    Returns:
        string (str): A GPX string for database storage or downloading.
    """
    gpx = gpxpy.gpx.GPX()
    gpx_track = gpxpy.gpx.GPXTrack()
    gpx.tracks.append(gpx_track)
    gpx_segment = gpxpy.gpx.GPXTrackSegment()
    gpx_track.segments.append(gpx_segment)
    for point_dict in json_data:

        for _, point in point_dict.items():
            time = datetime.fromisoformat(point["time"].replace("Z", "+00:00"))
            gpx_point = gpxpy.gpx.GPXTrackPoint(
                time=time,
                latitude=point["lat"],
                longitude=point["long"]
            )

            telemetry_data = Element("TelemetryData")
            for key, value in point["telemetry"].items():
                data_element = Element(key)
                data_element.text = str(value)
                telemetry_data.append(data_element)

            gpx_point.extensions.append(telemetry_data)
            gpx_segment.points.append(gpx_point)

    return gpx.to_xml()
