import boto3
import os

def load_config():
    """
    Fetch all app secrets from AWS Parameter Store.
    EC2 instance uses IAM role — no credentials needed in code.
    """
    ssm = boto3.client('ssm', region_name='ap-south-1')

    # fetch all parameters under /stock-agent/ path at once
    response = ssm.get_parameters_by_path(
        Path='/stock-agent/',
        WithDecryption=True  # decrypt SecureString parameters
    )

    # set each parameter as environment variable
    for param in response['Parameters']:
        # /stock-agent/OPENAI_API_KEY → OPENAI_API_KEY
        key = param['Name'].split('/')[-1]
        os.environ[key] = param['Value']

    print("[config] Secrets loaded from Parameter Store successfully")


def get(key: str) -> str:
    """Get a config value from environment."""
    value = os.environ.get(key)
    if not value:
        raise ValueError(f"Config key '{key}' not found — was load_config() called?")
    return value