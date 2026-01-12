"""
Configuration for Slack API scraper.

Instructions:
1. Copy .env.example to .env
2. Add your tokens to .env
3. Add user IDs to MONITOR_USERS below
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# =============================================================================
# TOKENS
# =============================================================================

# Bot Token (xoxb-...) - For presence monitoring and user info
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")

# User Token (xoxp-...) - For messages, search, and channels
SLACK_USER_TOKEN = os.getenv("SLACK_USER_TOKEN")

# =============================================================================
# USERS TO MONITOR
# =============================================================================

# Add user IDs here. To find a user ID:
# 1. Click on their profile in Slack
# 2. Click "View full profile"
# 3. Click "..." (more options)
# 4. Click "Copy member ID"
#
# Example: "U01ABC123DE"

MONITOR_USERS = [
    # "U01ABC123DE",  # John Smith
    # "U02XYZ456FG",  # Jane Doe
]

# =============================================================================
# SETTINGS
# =============================================================================

# How often to check presence (in seconds)
# Recommended: 180 (3 minutes) to respect rate limits
MONITOR_INTERVAL = 180
