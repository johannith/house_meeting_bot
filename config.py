import os
from dotenv import load_dotenv

def load_config():
    """Load configuration from environment variables."""
    load_dotenv()
    required_vars = [
        'SMTP_SERVER',
        'SMTP_PORT',
        'SMTP_USER',
        'SMTP_PASSWORD',
        'RECIPIENT_EMAIL',
        'NOTION_TOKEN',
        'HOUSE_MEETING_DATABASE_ID',
        'HOUSE_PROJECTS_DATABASE_ID'
    ]
    config = {}
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if value is None:
            missing_vars.append(var)
        config[var] = value
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
    return config 