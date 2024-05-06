import csv
import datetime
from datetime import datetime
import logging
import time
from statistics import mean

import gym
import numpy as np
from gym import spaces
from gym.utils import seeding

from utils.kube_watcher import get_pod_info, scheduler_watcher, schedule_pod
from utils.prometheus_metrics import get_application_latency
from utils.save_csv import save_to_csv

# Action Moves
ACTIONS = ["worker-1", "worker-2", "worker-3"]
NACTIONS = 3
MAX_STEPS = 10
MAX_SPREAD = 2  # fault-tolerant

APPS = [
    "frontend",
    "recommendationservice",
    "cartservice",
    "productcatalogservice",
    "adservice",
    "shippingservice",
    "checkoutservice",
    "emailservice",
    "paymentservice",
    "currencyservice",
]


class LatencyAware(gym.Env):
    """Horizontal Scaling for Online Boutique in Kubernetes - an OpenAI gym environment"""

    metadata = {"render.modes": ["human", "ansi", "array"]}

    def __init__(self, waiting_period=0.3, namespace="default"):
        # Define action and observation space
        # They must be gym.spaces objects

        super(LatencyAware, self).__init__()

        self.name = "online_boutique_gym"
        self.__version__ = "0.0.1"
        self.seed()
        self.namespace = namespace
        self.current_pod = {}
        self.pod_scheduled = []
        self.waiting_period = waiting_period  # seconds to wait after action

        # Current Step
        self.current_step = 0

        # Multi-Discrete
        # Deployment: Discrete 11
        # Action: Discrete 9 - None[0], Add-1[1], Add-2[2], Add-3[3], Add-4[4],
        #                      Stop-1[5], Stop-2[6], Stop-3[7], Stop-4[8]

        self.action_space = spaces.Discrete(NACTIONS)
        self.observation_space = self.get_observation_space()
        # Action and Observation Space
        # logging.info("[Init] Action Spaces: " + str(self.action_space))
        # logging.info("[Init] Observation Spaces: " + str(self.observation_space))

        # Info
        self.total_reward = None
        self.avg_latency = []

        # episode over
        self.episode_over = False
        self.info = {}

        self.time_start = 0
        self.execution_time = 0
        self.episode_count = 0
        self.file_results = "data/results.csv"

    # revision here!
    def step(self, action):
        if self.current_step == 1:
            self.time_start = time.time()

        # Execute one time step within the environment
        self.take_action(action)

        # Get reward
        reward = self.get_reward(action)
        self.total_reward += reward

        # Print Step and Total Reward
        # if self.current_step == MAX_STEPS:
        logging.info(
            "[Step {}] | Action (Node): {} | Reward: {} | Total Reward: {}".format(
                self.current_step,
                ACTIONS[action],
                reward,
                self.total_reward,
            )
        )

        self.info = dict(
            total_reward=self.total_reward,
        )

        if self.current_step == MAX_STEPS:
            logging.info(
                "[Episode {}] | Total Reward: {}".format(
                    self.episode_count, self.total_reward
                )
            )
            self.episode_count += 1
            self.execution_time = time.time() - self.time_start
            self.episode_over = True
            save_to_csv(
                self.file_results,
                self.episode_count,
                self.avg_latency,
                self.total_reward,
                self.execution_time,
            )
        self.watch_scheduling_queue()
        ob = self.get_state()
        logging.info("[Step {}] | State: {}".format(self.current_step, ob))

        # return ob, reward, self.episode_over, self.info
        return np.array(ob), reward, self.episode_over, self.info

    def seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    def reset(self):
        """
        Reset the state of the environment and returns an initial observation.
        Returns
        -------
        observation (object): the initial observation of the space.
        """
        self.current_step = 0
        self.episode_over = False
        self.total_reward = 0
        self.avg_latency = 0
        self.pod_scheduled = []
        self.watch_scheduling_queue()

        return np.array(self.get_state())

    def render(self, mode="human", close=False):
        # Render the environment to the screen
        return

    def take_action(self, action):
        self.current_step += 1
        logging.info("Action: %s", action)
        node_name = ACTIONS[action]
        schedule_pod(self.current_pod["pod_name"], node_name, self.namespace)

    def get_reward(self, action):
        """Calculate Rewards"""
        # Reward based on Keyword!
        logging.info("Entrou no get_reward")
        ob = self.get_state()
        app_item = APPS.index(self.current_pod["app_name"])

        init_index = app_item * 5
        node_list = ob[init_index + 2 : init_index + 5]
        selected_node = node_list[action]
        pod_spread = 0

        for node in node_list:
            spread_difference = selected_node - node
            if spread_difference > pod_spread:
                pod_spread = spread_difference

        logging.info("Pod Spread: %s", pod_spread)
        if self.current_step == MAX_STEPS:
            time.sleep(60)
            reward = get_application_latency(self.namespace)
            self.avg_latency = reward
            if pod_spread > MAX_SPREAD:
                reward += reward * 0.1
        else:
            reward = 0
            if pod_spread > MAX_SPREAD:
                reward += get_application_latency(self.namespace) * 0.1

        return -reward

    def get_state(self):

        ob = get_pod_info(
            self.current_pod["pod_name"], self.current_pod["app_name"], self.namespace
        )

        return ob

    def watch_scheduling_queue(self):
        self.current_pod = scheduler_watcher(self.namespace)
        # Avoid scheduling the same pod
        while self.current_pod["pod_name"] in self.pod_scheduled:
            self.current_pod = scheduler_watcher(self.namespace, self.pod_scheduled)

        self.pod_scheduled.append(self.current_pod["pod_name"])

    def get_observation_space(self):
        return spaces.Box(
            low=np.zeros(50),
            high=np.array(
                [
                    1,  # Current Pod  -- 1) recommendationservice
                    10,  # Desired Replicas
                    10,  # Pod on Worker-1
                    10,  # Pod on Worker-2
                    10,  # Pod on Worker-3
                    1,  # Current Pod -- 2) productcatalogservice
                    10,  # Desired Replicas
                    10,  # Pod on Worker-1
                    10,  # Pod on Worker-2
                    10,  # Pod on Worker-3
                    1,  # Current Pod -- 3) cartservice
                    10,  # Desired Replicas
                    10,  # Pod on Worker-1
                    10,  # Pod on Worker-2
                    10,  # Pod on Worker-3
                    1,  # Current Pod -- 4) adservice
                    10,  # Desired Replicas
                    10,  # Pod on Worker-1
                    10,  # Pod on Worker-2
                    10,  # Pod on Worker-3
                    1,  # Current Pod -- 5) paymentservice
                    10,  # Desired Replicas
                    10,  # Pod on Worker-1
                    10,  # Pod on Worker-2
                    10,  # Pod on Worker-3
                    1,  # Current Pod -- 6) shippingservice
                    10,  # Desired Replicas
                    10,  # Pod on Worker-1
                    10,  # Pod on Worker-2
                    10,  # Pod on Worker-3
                    1,  # Current Pod -- 7) currencyservice
                    10,  # Desired Replicas
                    10,  # Pod on Worker-1
                    10,  # Pod on Worker-2
                    10,  # Pod on Worker-3
                    1,  # Current Pod -- 8) checkoutservice
                    10,  # Desired Replicas
                    10,  # Pod on Worker-1
                    10,  # Pod on Worker-2
                    10,  # Pod on Worker-3
                    1,  # Current Pod -- 9) frontend
                    10,  # Desired Replicas
                    10,  # Pod on Worker-1
                    10,  # Pod on Worker-2
                    10,  # Pod on Worker-3
                    1,  # Current Pod -- 10) emailservice
                    10,  # Desired Replicas
                    10,  # Pod on Worker-1
                    10,  # Pod on Worker-2
                    10,  # Pod on Worker-3
                ]
            ),
            dtype=np.int32,
        )
