import pyproj
from shapely.ops import transform
from shapely.geometry import Point, LineString, shape

project = pyproj.Transformer.from_proj(
    pyproj.Proj("epsg:4326"),  # source coordinate system
    pyproj.Proj("epsg:900913"),
    always_xy=True,
)  # destination coordinate system

transformedPoint1 = transform(project.transform, Point(77.5946, 12.9716))

# transformedPoint2 = transform(project.transform, Point(1, 2))

# print(transformedPoint1.distance(transformedPoint2))

# print(round(transformedPoint1.x, 4), ',', round(transformedPoint1.y, 4))

print(f'{round(transformedPoint1.x, 4)} m, {round(transformedPoint1.y, 4)} m')