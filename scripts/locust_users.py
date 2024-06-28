import requests
import random
from time import sleep

URL = "http://10.2.33.221:30949/swarm"
MIN_USERS = 5
MAX_USERS = 300 
# 50 - 100 - 50 - 150 - 50 - 250 - 50 - 350 - 50 - 400



# def change_user():
#     while True:
#         user_up = 50
#         current_user = MIN_USERS
#         waiting_period = 0
#         for x in range(1, 9):
#             print(x)
#             try:
#                 spawn_rate = 2
#                 if x % 2 == 0:
#                     user_up += 100
#                     if user_up > MAX_USERS:
#                         user_up = MAX_USERS
#                     current_user = user_up
#                     waiting_period = (user_up / spawn_rate) + 20 
#                 else:
#                     current_user = MIN_USERS
#                     waiting_period = 50
#                     spawn_rate = 100
#                 payload = {
#                     "user_count": current_user,
#                     "spawn_rate": spawn_rate,
#                 }
#                 response = requests.post(URL, data=payload)
#                 print(f"Users: {current_user}")
#                 sleep(waiting_period)
#             except Exception as e:
#                 print(e)


def change_user():
    while True:
        user_up = 0
        current_user = MIN_USERS
        waiting_period = 0
        for x in range(0, 7):
            print(x)
            try:
                spawn_rate = 1
                if x == 0:
                    current_user = MIN_USERS
                    waiting_period = 300
                    spawn_rate = 1
                if x >= 1:
                    user_up += 50
                    if user_up > MAX_USERS:
                        user_up = MAX_USERS
                    current_user = user_up
                    waiting_period = 120
                payload = {
                    "user_count": current_user,
                    "spawn_rate": spawn_rate,
                }
                response = requests.post(URL, data=payload)
                print(f"Users: {current_user}")
                sleep(waiting_period)
            except Exception as e:
                print(e)



if __name__ == "__main__":
    change_user()
