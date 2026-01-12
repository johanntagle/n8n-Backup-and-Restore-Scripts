"""
N8N Configuration Loader
Loads configuration from .env file with environment variable overrides
"""

import os
from pathlib import Path
from typing import Optional


class N8NConfig:
    """Configuration manager for N8N backup/restore scripts"""

    def __init__(self, config_file: Optional[Path] = None):
        """
        Initialize configuration

        Args:
            config_file: Path to configuration file. If None, looks for .env in script directory
        """
        if config_file is None:
            # Look for .env in the current directory or the script directory
            config_file = self._find_config_file()

        self.config_file = config_file
        self._load_config()

    def _find_config_file(self) -> Optional[Path]:
        """Find configuration file in standard locations"""
        possible_locations = [
            Path.cwd() / ".env",
            Path(__file__).parent / ".env",
            Path.home() / ".n8n" / ".env",
        ]

        for location in possible_locations:
            if location.exists():
                return location

        return None

    def _load_config(self):
        """Load configuration from file"""
        self.config = {}

        if self.config_file and self.config_file.exists():
            with open(self.config_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    # Skip comments and empty lines
                    if not line or line.startswith('#'):
                        continue
                    # Parse KEY=VALUE format
                    if '=' in line:
                        key, value = line.split('=', 1)
                        self.config[key.strip()] = value.strip()

    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """
        Get configuration value

        Priority:
        1. Environment variable (highest)
        2. Configuration file
        3. Default value (lowest)

        Args:
            key: Configuration key
            default: Default value if not found

        Returns:
            Configuration value
        """
        # First check environment variable
        env_value = os.environ.get(key)
        if env_value is not None:
            return env_value

        # Then check config file
        if key in self.config:
            return self.config[key]

        # Finally return default
        return default

    def get_required(self, key: str) -> str:
        """
        Get required configuration value

        Args:
            key: Configuration key

        Returns:
            Configuration value

        Raises:
            ValueError: If configuration value is not found
        """
        value = self.get(key)
        if not value:
            raise ValueError(f"Required configuration '{key}' not found. "
                           f"Set it in .env file or as environment variable.")
        return value


# Global configuration instance
_config = None


def get_config(config_file: Optional[Path] = None) -> N8NConfig:
    """Get or create global configuration instance"""
    global _config
    if _config is None:
        _config = N8NConfig(config_file)
    return _config


def get_n8n_api_url() -> str:
    """Get N8N API URL from configuration (required)"""
    config = get_config()
    return config.get_required("N8N_API_URL")


def get_n8n_api_key() -> str:
    """Get N8N API Key from configuration (required)"""
    config = get_config()
    return config.get_required("N8N_API_KEY")


def get_backup_dir(default=None) -> Path:
    """Get backup directory from configuration"""
    config = get_config()
    backup_dir_str = config.get("BACKUP_DIR")
    if backup_dir_str:
        return Path(backup_dir_str)
    elif default:
        return default
    else:
        return Path.home() / "n8n-workflows-backup"
