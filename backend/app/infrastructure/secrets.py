import os
from typing import Optional


def _read_file(path: str) -> Optional[str]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except Exception:
        return None


def _read_ssm(path: str) -> Optional[str]:
    # Lazy import to avoid boto3 dependency at import time
    try:
        import boto3  # type: ignore
        from botocore.exceptions import BotoCoreError, ClientError  # type: ignore
    except Exception:
        return None
    try:
        ssm = boto3.client("ssm")
        resp = ssm.get_parameter(Name=path, WithDecryption=True)
        return resp.get("Parameter", {}).get("Value")
    except (BotoCoreError, ClientError):
        return None


def get_secret(name: str, default: Optional[str] = None) -> Optional[str]:
    """Resolve a secret by name using common strategies:

    Priority:
    1) ${NAME}_FILE -> read contents from file (Docker secrets)
    2) /run/secrets/${name} file (Docker secrets default path)
    3) ${NAME}_SSM_PATH -> fetch from AWS SSM Parameter Store (decrypted)
    4) ${NAME} -> plain environment variable
    5) default
    """
    file_env = os.getenv(f"{name}_FILE")
    if file_env:
        v = _read_file(file_env)
        if v:
            return v

    v = _read_file(f"/run/secrets/{name}")
    if v:
        return v

    ssm_path = os.getenv(f"{name}_SSM_PATH")
    if ssm_path:
        v = _read_ssm(ssm_path)
        if v:
            return v

    env = os.getenv(name)
    if env:
        return env
    return default
