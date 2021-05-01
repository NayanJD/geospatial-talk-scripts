from shapely.geometry import Point, LineString, shape
from shapely.ops import transform
from functools import cmp_to_key
from math import pi, sqrt, cos, sin
import pyproj
import random
import asyncio
import websockets
import json
import threading
import argparse

parser = argparse.ArgumentParser()
parser.add_argument(
    "-t", "--threads", type=int, help="specify no of threads. defaults to 1"
)
parser.add_argument(
    "-d",
    "--cred-dir",
    type=str,
    help="specify credential json file. defaults to creds.json",
)

args = parser.parse_args()

no_of_threads = 1
creds_file_path = "./creds.json"

if args.threads:
    no_of_threads = args.threads
if args.cred_dir:
    creds_file_path = args.cred_dir

# print('threads:: ',args.threads)
# print('cred-dir:: ', args.cred_dir)

cred_data = None
with open(creds_file_path) as f:
    # print(f.readlines())
    cred_data = json.load(f)


with open("./poly1.json") as f:
    poly = shape(json.loads(f.read()))

    center = poly.centroid

    print(center.x)


def get_random_point_in_circle(X, Y, R, n):
    points = []
    for i in range(n):
        # print(random.uniform(0,1))
        t = 2 * pi * random.uniform(0, 1)
        r = R * random.uniform(0, 1)

        x = X + r * cos(t)
        y = Y + r * sin(t)
        points.append(Point(x, y))

    return points


def get_random_point_in_polygon(poly):
    minx, miny, maxx, maxy = poly.bounds
    while True:
        p = Point(random.uniform(minx, maxx), random.uniform(miny, maxy))
        if poly.contains(p):
            return p


def get_random_points_on_line(point1, point2):
    line = LineString([point1, point2])
    linePoints = []
    for i in range(10):
        pt = line.interpolate(random.random(), True)
        # lineCoords.append([pt.x, pt.y])
        linePoints.append(pt)

    def compare(x, y):
        return x.distance(point1) - y.distance(point1)

    sorted_line_points = sorted(linePoints, key=cmp_to_key(compare))

    return [[point.x, point.y] for point in sorted_line_points]


def generate_random(number):
    points = []
    minx, miny, maxx, maxy = (-90, -45, 90, 45)
    while len(points) < number:
        pnt = Point(random.uniform(minx, maxx), random.uniform(miny, maxy))
        # if polygon.contains(pnt):
        [(x, y)] = pnt.coords
        points.append([x, y])
    return points


# print(generate_random(4))
def getLatLongPayload(latitude, longitude):
    return json.dumps(
        {"type": "location_update", "latitude": latitude, "longitude": longitude}
    )


transformCoordinateSystemTo = pyproj.Transformer.from_proj(
    pyproj.Proj("epsg:4326"),  # source coordinate system
    pyproj.Proj("epsg:900913"),
    always_xy=True,
).transform

transformCoordinateSystemFrom = pyproj.Transformer.from_proj(
    pyproj.Proj("epsg:900913"),  # source coordinate system
    pyproj.Proj("epsg:4326"),
    always_xy=True,
).transform


async def hello(thread_no):
    print("thread_no:: ", thread_no)
    uri = "ws://127.0.0.1:8000/ws/location_update"
    async with websockets.connect(uri, ping_interval=None) as websocket:
        # name = input("What's your name? ")

        username = cred_data[thread_no]["username"]
        password = cred_data[thread_no]["password"]

        auth_payload = json.dumps(
            {"type": "auth", "username": username, "password": password}
        )

        try:
            await websocket.send(auth_payload)
        except Exception as e:
            print(e)
            return

        auth_text = await websocket.recv()
        auth_data = json.loads(auth_text)

        if auth_data["auth_status"] == "unauthenticated":
            print(f"thread {thread_no}:: Not authenticated. Cancelling...")
            return

        # event = threading.Event()

        # async def ping():
        # [[x1, y1]] = generate_random(1)
        # [[x2, y2]] = generate_random(1)

        # lineCoords = []
        # line = LineString([(x1, y1), (x2, y2)])
        # for i in range(10):
        #     pt = line.interpolate(random.random(), True)
        #     lineCoords.append([pt.x, pt.y])

        # Approach 2
        # point1 = get_random_point_in_polygon(poly)
        # point2 = get_random_point_in_polygon(poly)
        # lineCoords = get_random_points_on_line(point1, point2)

        # Approach 3
        _, _, maxx, maxy = poly.bounds

        tangent = sqrt(maxx ** 2 + maxy ** 2)

        # distance = center.distance(Point(maxx, maxy))

        transformedCenter = transform(transformCoordinateSystemTo, center)
        transformedMaxPoint = transform(transformCoordinateSystemTo, Point(maxx, maxy))
        transformedPoly = transform(transformCoordinateSystemTo, poly)
        # print("distance ", transformedPoly.distance(transformedMaxPoint))
        # print("center ", transformedCenter.x, transformedCenter.y)
        distance = 500

        # distance = transformedCenter.distance(transformedMaxPoint)

        initial_point = None
        final_point = None

        [initial_point, final_point] = get_random_point_in_circle(
            transformedCenter.x, transformedCenter.y, distance, 2
        )
        lineCoords = get_random_points_on_line(initial_point, final_point)

        i = 0
        while True:
            # [[x, y]] = generate_random(1)

            # point = get_random_point_in_polygon(poly)

            # Approach 2
            # i = (i + 1) % len(lineCoords)

            if i == len(lineCoords):
                initial_point = final_point
                [final_point] = get_random_point_in_circle(
                    transformedCenter.x, transformedCenter.y, distance, 1
                )
                lineCoords = get_random_points_on_line(initial_point, final_point)
                i = 0

            [x, y] = lineCoords[i]
            
            transformedPoint = transform(transformCoordinateSystemFrom, Point(x, y))
            location_payload = getLatLongPayload(transformedPoint.x, transformedPoint.y)

            await websocket.send(location_payload)

            print(f"thread {thread_no}:: Sending coords", location_payload)

            await asyncio.sleep(0.5)

            i = i + 1


async def main():
    tasks = []
    for _ in range(1):
        for i in range(no_of_threads):
            tasks.append(asyncio.create_task(hello(i)))

    await asyncio.gather(*tasks)


# asyncio.get_event_loop().run_until_complete(hello())

asyncio.run(main())

# point1 = get_random_point_in_polygon(poly)
# point2 = get_random_point_in_polygon(poly)

# print(get_random_points_on_line(point1, point2))

# location_payload = getLatLongPayload(point.x, point.y)
