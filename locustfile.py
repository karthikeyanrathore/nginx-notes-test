import time, random, string
from locust import HttpUser, task, between
from locust.exception import  InterruptTaskSet

NOTES_CHAR_LEN = 100
USERNAME_CHAR_LEN = 8

class HelloWorldUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        SIGNUP_URI = "/api/auth/signup"
        # First register an account then get access token
        # after logging in.
        ascii = string.ascii_letters
        self.username = "".join([random.choice(ascii) for _ in range(USERNAME_CHAR_LEN)])
        payload = {"username":self.username, "password":"bar"}
        resp = self.client.post(SIGNUP_URI, json=payload)
        assert int(resp.status_code) == 200, f"error"
        # print(resp.json())
        if not isinstance(resp.json(), dict):
            raise InterruptTaskSet()
        LOGIN_URI = "/api/auth/login"
        resp = self.client.post(LOGIN_URI, json=payload)
        # print(resp.json())
        assert int(resp.status_code) == 200, f"error"
        # print(resp.json())
        if not isinstance(resp.json(), dict):
            raise InterruptTaskSet()
        self.headers = {"Authorization": "Bearer " + resp.json()["data"]["access_token"]}

    @task
    def initialize(self):
        NOTES_BP = "/api/notes"
        ascii = string.ascii_letters
        payload = {"note": "".join([random.choice(ascii) for _ in range(NOTES_CHAR_LEN)])}
        self.client.post(NOTES_BP, json=payload, headers=self.headers)
        self.client.get(NOTES_BP, headers=self.headers)
    



# docker-compose down -v; docker-compose build;docker-compose up -d; docker-compose logs  -f notes-api
# locust -f locustfile.py  -H http://0.0.0.0:80 --users 1 --spawn-rate 1

# AIM is find bottleneck in your app?
# yt conference: https://www.youtube.com/watch?v=XjSEgiFDARw&ab_channel=FOSDEM
# 1. How to assess ? 
#     1a. Performance Testing
#     1b. Load Testing
#     1c. Stress Testing

# 2. Performance Testing
#     2a. no heavy load 
#     2b. establish a benchmark behavior.

# 3. Load Testing
#     3a. gradualy increase load
#     3b. simulate virtual users
#     3c. it can find memory leaks, network issues, buffer overflow?
#     3d. you may run into database issue as it has a upper limit.
#     3e. aim is to find the bottleneck in the system by breaking it.

# 4. Stress Testing
#     4a. similar to load testing.
#     4b. ...


# NOTE: isolate the testing environment. 
# Please don't do the testing on the same machine where your application is running.