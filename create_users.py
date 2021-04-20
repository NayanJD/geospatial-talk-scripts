import requests
import json

r = requests.post(
    "http://127.0.0.1:8000/api/token",
    data={"username": "nayan", "password": "Temple12"},
)


print(r.status_code)
print(r.text)

auth_data = json.loads(r.text)
token = auth_data["access"]

password_data = []
for i in range(1, 101):
    username = f"nayan{i}"
    data = {"username": username, "password": "password"}
    r = requests.post(
        "http://127.0.0.1:8000/api/user",
        data=data,
        headers={"Authorization": f"Bearer {token}"},
    )

    password_data.append(data)

    print(r.status_code)

with open("./creds.json", "w") as f:
    f.write(json.dumps(password_data))
