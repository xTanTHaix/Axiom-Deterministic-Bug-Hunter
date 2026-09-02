"""
axiom.config module

Configuration management for Axiom Aegis
"""

from pathlib import Path
from typing import Dict, Any, Optional
import os


class Config:
    """Main configuration class"""

    def __init__(self):
        """Initialize configuration"""
        self._config: Dict[str, Any] = {}
        self._load_env()

    def _load_env(self, env_path: Optional[str] = None) -> None:
        """Load configuration from .env file

        Args:
            env_path: Optional path to env file. Defaults to '.env'.
        """
        env_file = Path(env_path) if env_path else Path('.env')

        if env_file.exists():
            try:
                with open(env_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()

                        # Skip comments and empty lines
                        if not line or line.startswith('#'):
                            continue

                        # Parse KEY=VALUE
                        if '=' in line:
                            key, value = line.split('=', 1)
                            self._config[key.strip()] = value.strip()
            except IOError:
                pass

    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get configuration value"""
        return self._config.get(key, default)

    def set(self, key: str, value: str) -> None:
        """Set configuration value"""
        self._config[key] = value

    def to_dict(self) -> Dict[str, Any]:
        """Return configuration as dictionary"""
        return self._config.copy()


def load_config(env_file: Optional[str] = None) -> Config:
    """
    Load configuration

    Args:
        env_file: Path to .env file (default: '.env')

    Returns:
        Config instance
    """
    config = Config()

    if env_file:
        config._load_env(env_file)

    return config


__all__ = [
    'Config',
    'load_config',
]
