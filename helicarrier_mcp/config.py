import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    api_url: str = os.environ.get(
        "HELICARRIER_API_URL", "https://helicarrier-dev.zingworks.com/api"
    )
    gcp_project: str = os.environ.get("GCP_PROJECT", "kf-dev-ops-p001")
    secret_name: str = os.environ.get(
        "API_KEY_SECRET", "helicarrier-health-check-api-key"
    )
    firestore_database: str = os.environ.get(
        "FIRESTORE_DATABASE", "helicarrier-development"
    )


config = Config()
