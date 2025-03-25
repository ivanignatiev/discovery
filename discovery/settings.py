from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class DiscoverySettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='discovery_', case_sensitive=False, env_file=".env")

    extract_target_folder_path: str = Field('.')

    azure_openai_deployment_name: str = Field()
    azure_openai_endpoint: str = Field()
    azure_openai_key: str = Field()
    azure_openai_api_version: str = Field()

def get_settings() -> DiscoverySettings:
    return DiscoverySettings()