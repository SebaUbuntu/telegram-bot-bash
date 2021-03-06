"""Homebot module."""

__version__ = "4.0.0"

# We really need a config file, import it at module start
from config import config
from homebot.core.mdlintf import register_modules
from pathlib import Path

# Silence wench
config = config

bot_path = Path(__file__).parent
modules_path = bot_path / "modules"

register_modules(modules_path)
