import yaml
from pathlib import Path
from pydantic_settings import BaseSettings

class Config(BaseSettings):
    alpha_decay: int = 120
    sigma_grid: dict = {"min": -4.0, "max": 4.0, "step": 0.25}
    liquidity: dict
    particle: dict
    dealer: dict
    hazard: dict
    forward: dict
    db: dict
    api: dict

    @classmethod
    def load(cls):
        docker_path = Path("/app/config/default.yaml")
        local_path = Path("config/default.yaml")
        path = docker_path if docker_path.exists() else local_path
        with open(path, "r") as f:
            data = yaml.safe_load(f)
        return cls(**data)

class Symbols(BaseSettings):
    symbols: list

    @classmethod
    def load(cls):
        docker_path = Path("/app/config/symbols.yaml")
        local_path = Path("config/symbols.yaml")
        path = docker_path if docker_path.exists() else local_path
        with open(path, "r") as f:
            data = yaml.safe_load(f)
        return cls(**data)

settings = Config.load()
symbol_config = Symbols.load()