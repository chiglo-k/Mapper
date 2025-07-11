import toml
import os

dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(dir)
config_path = os.path.join(backend_dir, "config", "config.toml")
config = toml.load(config_path)

