import json
import requests


def get_ip_location(ip: str) -> dict:
    headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer {0'}
    api = f"http://api.ipstack.com/{ip}?access_key=31723cb5317b6589212b8d1a30aeef66"
    response = requests.get(api, headers=headers)
    if response.status_code == 200:
        return json.loads(response.content.decode('utf-8'))
    else:
        return None


session = {
    "user_id": None
}

ip_information = get_ip_location("86.81.160.217")
for x in ip_information:
    if x == "location":
        for y in ip_information[x]:
            if y == "languages":
                for z in ip_information[x][y][0]:
                    session[z] = ip_information[x][y][0][z]
            else:
                session[y] = ip_information[x][y]
    else:
        session[x] = ip_information[x]

print(session)
