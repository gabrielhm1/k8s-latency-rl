import numpy as np
from env import LatencyAware


class QLearningAgent:
    def __init__(self, env, learning_rate=0.1, discount_factor=0.99, epsilon=0.1):
        self.env = env
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.epsilon = epsilon
        self.action_space_size = env.action_space.n
        print(self.action_space_size)
        self.state_space_size = 1000

        # Initialize Q-table with zeros
        self.q_table = np.zeros((self.state_space_size, self.action_space_size))
        # print(self.q_table)

    def choose_action(self, state):
        print(f"Finding state: {state}")
        if np.random.rand() < self.epsilon:
            return np.random.choice(self.action_space_size)
        else:
            print(f"state_array: {self.q_table[state]}")
            print(f"argmax: {np.argmax(self.q_table[state])}")
            return np.argmax(self.q_table[state, :])

    def update_q_table(self, state, action, reward, next_state):
        best_next_action = np.argmax(self.q_table[next_state, :])
        td_target = (
            reward + self.discount_factor * self.q_table[next_state, best_next_action]
        )
        td_error = td_target - self.q_table[state, action]
        self.q_table[state, action] += self.learning_rate * td_error
        print(self.q_table)

    def train(self, episodes):
        for episode in range(episodes):
            state = self.env.reset()
            total_reward = 0

            while True:
                action = self.choose_action(state)
                next_state, reward, done, _ = self.env.step(action)
                total_reward += reward

                self.update_q_table(state, action, reward, next_state)

                state = next_state

                if done:
                    break

            print(f"Episode {episode + 1}, Total Reward: {total_reward}")


# Create an instance of the environment
env = LatencyAware(namespace="learning")

# Create an instance of the Q-learning agent
agent = QLearningAgent(env)
# print((agent.q_table[0]))
# Train the agent
agent.train(episodes=100)
