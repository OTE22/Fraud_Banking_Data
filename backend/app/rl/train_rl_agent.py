import numpy as np
from app.rl.banking_environment import BankingEnvironment


class QLearningAgent:
    def __init__(self, state_size: int, action_size: int = 2, learning_rate: float = 0.1, discount: float = 0.95):
        self.q_table = np.zeros((state_size, action_size))
        self.lr = learning_rate
        self.discount = discount

    def act(self, state_idx: int) -> int:
        return int(np.argmax(self.q_table[state_idx])) if np.random.random() > 0.1 else np.random.randint(2)

    def update(self, state: int, action: int, reward: float, next_state: int) -> None:
        old = self.q_table[state, action]
        next_max = np.max(self.q_table[next_state])
        self.q_table[state, action] = old + self.lr * (reward + self.discount * next_max - old)


def train_rl_agent(episodes: int = 100) -> QLearningAgent:
    env = BankingEnvironment()
    agent = QLearningAgent(state_size=env.num_features)
    for _ in range(episodes):
        state = env.reset()
        done = False
        while not done:
            state_idx = int(np.argmax(state))
            action = agent.act(state_idx)
            next_state, reward, done = env.step(action)
            next_idx = int(np.argmax(next_state))
            agent.update(state_idx, action, reward, next_idx)
            state = next_state
    return agent
