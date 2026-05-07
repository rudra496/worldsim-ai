"""Reinforcement Learning agents using Gymnasium (optional) with fallback."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)

HAS_GYMNASIUM = False
try:
    import gymnasium as gym
    from gymnasium import spaces
    HAS_GYMNASIUM = True
except ImportError:
    pass

HAS_SB3 = False
try:
    from stable_baselines3 import PPO
    HAS_SB3 = True
except ImportError:
    pass


class SimulationEnv:
    """
    Gymnasium-compatible environment wrapping SimulationEngine.
    
    Falls back to a simple NumPy-based environment if Gymnasium is unavailable.
    """

    def __init__(self, world_size: Tuple[int, int] = (20, 20), num_agents: int = 10,
                 max_steps: int = 200, seed: Optional[int] = 42):
        self.world_size = world_size
        self.num_agents = num_agents
        self.max_steps = max_steps
        self._step_count = 0
        self._rng = np.random.default_rng(seed)
        
        # State: agent positions (x, y) + resources
        self._agent_pos = self._rng.integers(0, max(world_size), size=(num_agents, 2))
        self._resources = self._rng.uniform(50, 100, size=num_agents)
        self._energy = self._rng.uniform(80, 100, size=num_agents)
        
        # Observation: flattened state
        obs_size = num_agents * 4  # x, y, resources, energy per agent
        self.observation_space = spaces.Box(low=0, high=max(world_size) * 2,
                                            shape=(obs_size,), dtype=np.float32) if HAS_GYMNASIUM else None
        self.action_space = spaces.Discrete(5 * num_agents) if HAS_GYMNASIUM else None
        # Actions per agent: 0=stay, 1=up, 2=down, 3=left, 4=right

    def _build_observation(self) -> np.ndarray:
        obs = np.concatenate([
            self._agent_pos.astype(np.float32) / max(self.world_size),
            self._resources.astype(np.float32) / 100.0,
            self._energy.astype(np.float32) / 100.0,
        ])
        return obs

    def reset(self, seed: Optional[int] = None, **kwargs) -> Tuple[np.ndarray, Dict]:
        if seed is not None:
            self._rng = np.random.default_rng(seed)
        self._step_count = 0
        self._agent_pos = self._rng.integers(0, max(self.world_size), size=(self.num_agents, 2))
        self._resources = self._rng.uniform(50, 100, size=self.num_agents)
        self._energy = self._rng.uniform(80, 100, size=self.num_agents)
        return self._build_observation(), {"step": 0}

    def step(self, action: int) -> Tuple[np.ndarray, float, bool, bool, Dict]:
        self._step_count += 1
        
        # Parse action: each agent gets one of 5 actions
        reward = 0.0
        for i in range(self.num_agents):
            agent_action = action % 5
            action = action // 5
            
            # Move
            if agent_action == 1: self._agent_pos[i, 1] = max(0, self._agent_pos[i, 1] - 1)
            elif agent_action == 2: self._agent_pos[i, 1] = min(self.world_size[1]-1, self._agent_pos[i, 1] + 1)
            elif agent_action == 3: self._agent_pos[i, 0] = max(0, self._agent_pos[i, 0] - 1)
            elif agent_action == 4: self._agent_pos[i, 0] = min(self.world_size[0]-1, self._agent_pos[i, 0] + 1)
            
            # Consume energy
            self._energy[i] = max(0, self._energy[i] - 0.5)
            
            # Produce resources (random event)
            if self._rng.random() < 0.1:
                self._resources[i] = min(100, self._resources[i] + 5)
            
            # Reward: resource production - energy waste
            reward += self._resources[i] / 100.0 - (1.0 - self._energy[i] / 100.0) * 0.5
        
        reward /= self.num_agents  # normalize
        
        # Terminal conditions
        terminated = bool(np.any(self._energy < 5))
        truncated = self._step_count >= self.max_steps
        
        info = {"step": self._step_count, "total_resources": float(np.sum(self._resources)),
                "avg_energy": float(np.mean(self._energy))}
        
        return self._build_observation(), reward, terminated, truncated, info

    def render(self) -> Dict[str, Any]:
        return {
            "agent_positions": self._agent_pos.tolist(),
            "resources": self._resources.tolist(),
            "energy": self._energy.tolist(),
            "step": self._step_count,
        }


class RLAgent:
    """
    RL agent that learns optimal policies.
    Uses PPO (stable-baselines3) if available, else random/epsilon-greedy.
    """

    def __init__(self, env: Optional[SimulationEnv] = None, strategy: str = "learned",
                 seed: int = 42):
        self._env = env
        self.strategy = strategy
        self._rng = np.random.default_rng(seed)
        self._model = None
        self._trained = False
        self._q_table: Dict[int, np.ndarray] = {}  # simple Q-learning fallback

    def train(self, env: Optional[SimulationEnv] = None, total_timesteps: int = 10000) -> Dict[str, Any]:
        """Train the RL agent."""
        env = env or self._env
        if env is None:
            return {"status": "no_env"}

        if HAS_SB3 and HAS_GYMNASIUM:
            try:
                self._model = PPO("MlpPolicy", env, verbose=0, seed=42)
                self._model.learn(total_timesteps=total_timesteps)
                self._trained = True
                return {"status": "trained", "method": "PPO", "timesteps": total_timesteps}
            except Exception as e:
                logger.warning(f"PPO training failed: {e}, falling back to Q-learning")

        # Q-learning fallback
        return self._q_learn(env, episodes=max(100, total_timesteps // 200))

    def _q_learn(self, env: SimulationEnv, episodes: int = 100) -> Dict[str, Any]:
        """Simple tabular Q-learning as fallback."""
        lr = 0.1
        gamma = 0.95
        epsilon = 1.0
        epsilon_decay = 0.995
        epsilon_min = 0.01
        
        rewards_history = []
        for ep in range(episodes):
            obs, _ = env.reset()
            total_reward = 0
            done = False
            
            while not done:
                # Discretize observation for Q-table
                state_key = int(np.sum(np.floor(obs * 10)) % 10000)
                
                if state_key not in self._q_table:
                    self._q_table[state_key] = np.zeros(env.action_space.n if env.action_space else 5)
                
                # Epsilon-greedy
                if self._rng.random() < epsilon:
                    action = self._rng.integers(0, env.action_space.n if env.action_space else 5)
                else:
                    action = int(np.argmax(self._q_table[state_key]))
                
                next_obs, reward, terminated, truncated, info = env.step(action)
                next_state_key = int(np.sum(np.floor(next_obs * 10)) % 10000)
                
                if next_state_key not in self._q_table:
                    self._q_table[next_state_key] = np.zeros(env.action_space.n if env.action_space else 5)
                
                # Q-update
                best_next = np.max(self._q_table[next_state_key])
                td_target = reward + gamma * best_next * (1 - terminated)
                self._q_table[state_key][action] += lr * (td_target - self._q_table[state_key][action])
                
                obs = next_obs
                total_reward += reward
                done = terminated or truncated
            
            epsilon = max(epsilon_min, epsilon * epsilon_decay)
            rewards_history.append(total_reward)
        
        self._trained = True
        return {
            "status": "trained", "method": "q_learning",
            "episodes": episodes,
            "avg_reward": float(np.mean(rewards_history[-20:])),
            "q_table_size": len(self._q_table),
        }

    def predict(self, observation: np.ndarray) -> int:
        """Select action given observation."""
        if HAS_SB3 and self._model and self._trained:
            action, _ = self._model.predict(observation, deterministic=True)
            return int(action)
        
        if self._trained and self._q_table:
            state_key = int(np.sum(np.floor(observation * 10)) % 10000)
            if state_key in self._q_table:
                return int(np.argmax(self._q_table[state_key]))
        
        # Random fallback
        return int(self._rng.integers(0, 5))

    def save(self, path: str) -> None:
        if HAS_SB3 and self._model and self._trained:
            self._model.save(path)
        else:
            import json
            # Save Q-table (sample to keep size manageable)
            sample = {str(k): v.tolist() for k, v in list(self._q_table.items())[:1000]}
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            Path(path).write_text(json.dumps({"q_table": sample, "strategy": self.strategy}))

    def load(self, path: str) -> None:
        if HAS_SB3:
            try:
                self._model = PPO.load(path)
                self._trained = True
                return
            except Exception:
                pass
        import json
        data = json.loads(Path(path).read_text())
        self._q_table = {int(k): np.array(v) for k, v in data.get("q_table", {}).items()}
        self._trained = len(self._q_table) > 0


class MultiAgentRLSystem:
    """
    Coordinate multiple RL agents with centralized training, decentralized execution.
    """

    def __init__(self, num_agents: int = 4, env: Optional[SimulationEnv] = None):
        self._agents = [RLAgent(env=env, strategy="learned", seed=i*100) for i in range(num_agents)]
        self._shared_buffer: List[Tuple[np.ndarray, int, float, np.ndarray, bool]] = []
        self._env = env

    def train_centralized(self, total_timesteps: int = 20000) -> Dict[str, Any]:
        """Train all agents in a shared environment."""
        env = self._env or SimulationEnv()
        results = {}
        for i, agent in enumerate(self._agents):
            result = agent.train(env=env, total_timesteps=total_timesteps // len(self._agents))
            results[f"agent_{i}"] = result
        results["system"] = "centralized_training_complete"
        return results

    def predict_batch(self, observation: np.ndarray) -> List[int]:
        """Get predictions from all agents."""
        return [agent.predict(observation) for agent in self._agents]

    def get_agent(self, index: int) -> RLAgent:
        return self._agents[index]
