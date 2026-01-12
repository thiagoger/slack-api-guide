"""
Slack API Scraper - Collect data from Slack using the official API.

Usage:
    python slack_scraper.py --presence              # Check user presence
    python slack_scraper.py --channels              # List all channels
    python slack_scraper.py --messages CHANNEL_ID   # Get channel messages
    python slack_scraper.py --search "query"        # Search messages
    python slack_scraper.py --users                 # List all users

Examples:
    python slack_scraper.py --presence
    python slack_scraper.py --messages C01ABC123 --limit 50
    python slack_scraper.py --search "budget report" --limit 20
"""

import argparse
from datetime import datetime

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

import config


# =============================================================================
# CLIENT SETUP
# =============================================================================

def get_bot_client():
    """Create a Slack client using the Bot token."""
    if not config.SLACK_BOT_TOKEN:
        raise ValueError(
            "SLACK_BOT_TOKEN not configured.\n"
            "1. Copy .env.example to .env\n"
            "2. Add your bot token (xoxb-...)"
        )
    return WebClient(token=config.SLACK_BOT_TOKEN)


def get_user_client():
    """Create a Slack client using the User token."""
    if not config.SLACK_USER_TOKEN:
        raise ValueError(
            "SLACK_USER_TOKEN not configured.\n"
            "1. Copy .env.example to .env\n"
            "2. Add your user token (xoxp-...)"
        )
    return WebClient(token=config.SLACK_USER_TOKEN)


# =============================================================================
# PRESENCE MONITORING
# =============================================================================

def get_user_presence(client, user_id):
    """
    Get the presence status of a user.

    Returns:
        "active" - Green dot (online and active)
        "away"   - Empty dot (inactive 10+ minutes)
        None     - Error occurred
    """
    try:
        response = client.users_getPresence(user=user_id)
        return response.get("presence", "unknown")
    except SlackApiError as e:
        print(f"  [ERROR] Getting presence for {user_id}: {e.response['error']}")
        return None


def get_user_info(client, user_id):
    """Get detailed information about a user."""
    try:
        response = client.users_info(user=user_id)
        user = response["user"]
        return {
            "id": user["id"],
            "name": user.get("name", ""),
            "real_name": user.get("real_name", ""),
            "email": user.get("profile", {}).get("email", ""),
            "title": user.get("profile", {}).get("title", ""),
            "is_admin": user.get("is_admin", False),
            "is_bot": user.get("is_bot", False),
        }
    except SlackApiError as e:
        print(f"  [ERROR] Getting user info for {user_id}: {e.response['error']}")
        return None


def check_presence():
    """Check presence for all monitored users."""
    if not config.MONITOR_USERS:
        print("\n  No users configured!")
        print("  Edit config.py and add user IDs to MONITOR_USERS\n")
        return

    client = get_bot_client()

    print(f"\n{'='*60}")
    print(f"  PRESENCE CHECK - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")

    for user_id in config.MONITOR_USERS:
        # Get user info for name
        info = get_user_info(client, user_id)
        name = info["real_name"] if info else user_id

        # Get presence
        presence = get_user_presence(client, user_id)

        # Format output
        icons = {
            "active": "[ONLINE]",
            "away": "[AWAY]  ",
        }
        icon = icons.get(presence, "[???]   ")

        print(f"  {icon} {name}")

    print(f"\n{'='*60}\n")


# =============================================================================
# USER OPERATIONS
# =============================================================================

def list_users():
    """List all users in the workspace."""
    client = get_bot_client()

    try:
        response = client.users_list()
        members = response["members"]

        # Filter out bots and deleted users
        real_users = [
            m for m in members
            if not m.get("is_bot") and not m.get("deleted")
        ]

        print(f"\n{'='*60}")
        print(f"  USERS ({len(real_users)} found)")
        print(f"{'='*60}\n")

        print(f"  {'ID':<12} | {'NAME':<25} | EMAIL")
        print(f"  {'-'*60}")

        for user in real_users:
            user_id = user["id"]
            name = user.get("real_name", user.get("name", ""))[:25]
            email = user.get("profile", {}).get("email", "")

            print(f"  {user_id:<12} | {name:<25} | {email}")

        print(f"\n{'='*60}\n")
        return real_users

    except SlackApiError as e:
        print(f"Error listing users: {e.response['error']}")
        return []


# =============================================================================
# CHANNEL OPERATIONS
# =============================================================================

def list_channels():
    """List all public channels in the workspace."""
    client = get_user_client()

    try:
        response = client.conversations_list(
            types="public_channel",
            limit=200
        )

        channels = response["channels"]

        print(f"\n{'='*60}")
        print(f"  CHANNELS ({len(channels)} found)")
        print(f"{'='*60}\n")

        print(f"  {'ID':<12} | {'NAME':<30} | MEMBERS")
        print(f"  {'-'*55}")

        for channel in channels:
            ch_id = channel["id"]
            name = f"#{channel['name']}"[:30]
            members = channel.get("num_members", "?")

            print(f"  {ch_id:<12} | {name:<30} | {members}")

        print(f"\n{'='*60}\n")
        return channels

    except SlackApiError as e:
        print(f"Error listing channels: {e.response['error']}")
        return []


def get_channel_messages(channel_id, limit=100):
    """
    Get messages from a channel.

    Args:
        channel_id: Channel ID (starts with C, D, or G)
        limit: Maximum messages to retrieve
    """
    client = get_user_client()

    try:
        response = client.conversations_history(
            channel=channel_id,
            limit=limit
        )

        messages = response["messages"]

        print(f"\n{'='*60}")
        print(f"  MESSAGES FROM {channel_id} ({len(messages)} retrieved)")
        print(f"{'='*60}\n")

        # Show oldest first
        for msg in reversed(messages):
            # Timestamp
            ts = float(msg.get("ts", 0))
            time_str = datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M")

            # User
            user = msg.get("user", msg.get("bot_id", "unknown"))

            # Text (truncate long messages)
            text = msg.get("text", "")
            if len(text) > 100:
                text = text[:100] + "..."

            print(f"  [{time_str}] {user}")
            print(f"    {text}")
            print()

        print(f"{'='*60}\n")
        return messages

    except SlackApiError as e:
        print(f"Error getting messages: {e.response['error']}")
        return []


# =============================================================================
# SEARCH
# =============================================================================

def search_messages(query, count=20):
    """
    Search for messages matching a query.

    Args:
        query: Search query (same syntax as Slack search)
        count: Number of results
    """
    client = get_user_client()

    try:
        response = client.search_messages(
            query=query,
            count=count,
            sort="timestamp",
            sort_dir="desc"
        )

        matches = response["messages"]["matches"]

        print(f"\n{'='*60}")
        print(f"  SEARCH: '{query}' ({len(matches)} results)")
        print(f"{'='*60}\n")

        for match in matches:
            # Timestamp
            ts = float(match.get("ts", 0))
            time_str = datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M")

            # Channel
            channel = match.get("channel", {}).get("name", "?")

            # User
            user = match.get("username", "?")

            # Text
            text = match.get("text", "")
            if len(text) > 100:
                text = text[:100] + "..."

            print(f"  [{time_str}] #{channel} - @{user}")
            print(f"    {text}")
            print()

        print(f"{'='*60}\n")
        return matches

    except SlackApiError as e:
        print(f"Error searching: {e.response['error']}")
        return []


# =============================================================================
# MAIN
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Slack API Scraper",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python slack_scraper.py --presence
  python slack_scraper.py --channels
  python slack_scraper.py --messages C01ABC123 --limit 50
  python slack_scraper.py --search "project update" --limit 10
        """
    )

    parser.add_argument(
        "--presence", action="store_true",
        help="Check presence status of monitored users"
    )
    parser.add_argument(
        "--users", action="store_true",
        help="List all users in the workspace"
    )
    parser.add_argument(
        "--channels", action="store_true",
        help="List all public channels"
    )
    parser.add_argument(
        "--messages", type=str, metavar="CHANNEL_ID",
        help="Get messages from a channel (use channel ID, e.g., C01ABC123)"
    )
    parser.add_argument(
        "--search", type=str, metavar="QUERY",
        help="Search messages"
    )
    parser.add_argument(
        "--limit", type=int, default=20,
        help="Number of results (default: 20)"
    )

    args = parser.parse_args()

    # Execute requested action
    if args.presence:
        check_presence()
    elif args.users:
        list_users()
    elif args.channels:
        list_channels()
    elif args.messages:
        get_channel_messages(args.messages, args.limit)
    elif args.search:
        search_messages(args.search, args.limit)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
