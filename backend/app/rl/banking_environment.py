import numpy as np


class BankingEnvironment:
    def __init__(self, num_features: int = 8):
        self.num_features = num_features
        self.state = np.zeros(num_features)
        self.step_count = 0

    def reset(self) -> np.ndarray:
        self.state = np.random.randn(self.num_features)
        self.step_count = 0
        return self.state

    def step(self, action: int) -> tuple[np.ndarray, float, bool]:
        self.step_count += 1
        reward = 1.0 if action == 1 else -0.1
        if action == 1:
            self.state += np.random.randn(self.num_features) * 0.1
        done = self.step_count >= 100
        return self.state, reward, done

    def render(self) -> None:
        print(f"Step: {self.step_count}, State mean: {self.state.mean():.3f}")
