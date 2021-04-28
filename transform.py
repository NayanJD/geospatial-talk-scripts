import pyproj
from shapely.ops import transform
from shapely.geometry import Point, LineString, shape

project = pyproj.Transformer.from_proj(
    pyproj.Proj("epsg:4326"),  # source coordinate system
    pyproj.Proj("epsg:900913"),
    always_xy=True,
)  # destination coordinate system

transformedPoint1 = transform(project.transform, Point(1, 1))

transformedPoint2 = transform(project.transform, Point(1, 2))

print(transformedPoint1.distance(transformedPoint2))