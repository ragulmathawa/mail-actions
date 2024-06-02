from gmail.mailbox import MailBox, MailBoxStats
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
import json as json
import os as os
from gmail.service import GMailService, Profile
import auth as auth
import progress.spinner as spinner
from ruleengine import RuleEngine
import ruleparser as ruleparser

def is_sync_needed(profile: Profile, stats: MailBoxStats):
    """
    Checks if synchronization is needed based on the gmail last History Id and mailbox lasistoryId stored in the database.

    Args:
        profile (Profile): The user's profile.
        stats (MailBoxStats): The statistics of the mailbox.

    Returns:
        bool: True if synchronization is needed, False otherwise.
    """
    return stats.get("lastHistoryId") is None or stats.get("lastHistoryId") != profile.get(
        "historyId"
    )


def print_welcome(profile: Profile, stats: MailBoxStats):
    print(f"\nWelcome {profile.get('emailAddress')}")
    print(f"Total messages: {profile.get('messagesTotal')}")

    if is_sync_needed(profile, stats):
        print(f"New Messages: {profile.get("messagesTotal") - stats.get('totalMessages')}")
        print(f"\nSYNC NEEDED\n")
    else:
        print("\nNo new messages\n")


def main():
    creds = auth.get_saved_credentials()
    if not creds:
        # if creds not found, get creds
        creds = auth.get_credentials()
        auth.save_credentials(creds)
    if not creds.valid:
        # if creds are not valid, refresh creds
        creds.refresh(Request())
        auth.save_credentials(creds)

    service = GMailService(creds)
    mailbox = MailBox(service)
    mailbox.init_db()
    rule_engine = RuleEngine(mailbox, service)
    stats = mailbox.get_stats()
    profile = service.get_profile()
    print_welcome(profile, stats)

    if is_sync_needed(profile, stats):
        mailbox.sync()
    try:
        rules = ruleparser.load_rules("rules.yaml")
        if len(rules) == 0:
            print("No rules found")
            return
        for rule in rules:
            print(f"Applying rule: {rule.get('name')}")
            rule_engine.apply_rule(rule)
    except Exception as e:
        raise e

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt as e:
        print("Exiting")
        pass
    
