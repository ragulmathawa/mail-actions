from sqlite3 import connect
import json as json
from typing import TypedDict
from gmail.service import GMailService, Message
from progress.bar import Bar
from progress.counter import Counter


from typing import TypedDict


class MailBoxStats(TypedDict):
    """
    Represents the statistics of a mailbox.

    Attributes:
        lastHistoryId (str): The last history ID of the mailbox.
        totalMessages (int): The total number of messages in the mailbox.
    """

    lastHistoryId: str
    totalMessages: int


class MailBox:
    """
    Represents a mailbox.

    Attributes:
        gmail_service (GMailService): The Gmail service to use for interacting with the mailbox.

    init_db() must be called before using the mailbox.
    """

    def __init__(self, gmailService: GMailService) -> None:
        self.gmail_service = gmailService
        pass

    def init_db(self):
        """
        Initializes the database by creating the necessary tables if they don't exist.
        """
        with connect("store.db") as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS messages (
                    id TEXT PRIMARY KEY,
                    threadId TEXT,
                    historyId TEXT,
                    internalDate TEXT,
                    labelIds TEXT,
                    payload__body__data TEXT,
                    payload__body__size INTEGER,
                    payload__body__attachmentId TEXT,
                    payload__filename TEXT,
                    payload__mimeType TEXT,
                    payload__partId TEXT,
                    payload__parts TEXT,
                    raw TEXT,
                    sizeEstimate INTEGER,
                    snippet TEXT
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS headers (
                    id INTEGER PRIMARY KEY,
                    message_id TEXT,
                    name TEXT,
                    value TEXT,
                    FOREIGN KEY (message_id) REFERENCES messages(id)
                )
                """
            )
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_headers_message_id ON headers (message_id)
                """
            )
            conn.commit()
        pass

    def get_stats(self) -> MailBoxStats:
        """
        Retrieves the statistics of the mailbox.

        Returns:
            A MailBoxStats object containing the last history ID and the total number of messages.
        """
        with connect("store.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT MAX(historyId) FROM messages")
            lastHistoryId = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM messages")
            totalMessages = cursor.fetchone()[0]
        return MailBoxStats(lastHistoryId=lastHistoryId, totalMessages=totalMessages)

    def sync(self):
        """
        Synchronizes the mailbox by comparing the remote and local message IDs.
        Fetches new messages and deletes messages that are no longer present remotely.

        This is a not a perfect implementation.
        Ideally, we need a full sync on the first time and then incremental syncs based on historyId.

        Returns:
            None
        """
        remoteIds = self.scan_remote()
        dbIds = self.scan_db()
        newMsgs = remoteIds - dbIds
        deletedMsgs = dbIds - remoteIds
        if len(newMsgs) > 0:
            self.fetch_messages(newMsgs)
        if len(deletedMsgs) > 0:
            self.delete_messages(deletedMsgs)
        print("Sync Completed")
        pass

    def delete_messages(self, ids: set[str]):
        """
        Deletes the specified messages from the mailbox.

        Args:
            ids (set[str]): The set of message IDs to delete.

        Returns:
            int: The number of messages deleted.
        """
        deleted = 0
        progress = Bar("Deleting messages", max=len(ids))
        for id in ids:
            with connect("store.db") as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM messages WHERE id=?", (id,))
                cursor.execute("DELETE FROM headers WHERE message_id=?", (id,))
                conn.commit()
            deleted = deleted + 1
            progress.next()
        progress.finish()
        return deleted

    def fetch_messages(self, ids: set[str]):
        """
        Fetches messages from the mailbox using the provided message IDs.

        Args:
            ids (set[str]): A set of message IDs to fetch.

        Returns:
            int: The number of messages successfully fetched and saved.
        """
        saved = 0
        bar = Bar("Fetching messages", max=len(ids))
        for id in ids:
            msg = self.gmail_service.get_message(id)
            self.save_message(msg)
            bar.next()
            saved = saved + 1
        bar.finish()
        return saved

    def save_message(self, msg: Message):
        """
        Saves the provided message to the database.

        Args:
            msg (Message): The message to be saved.

        Returns:
            None
        """
        with connect("store.db") as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO messages (
                    id,
                    threadId,
                    historyId,
                    internalDate,
                    labelIds,
                    payload__body__data,
                    payload__body__size,
                    payload__body__attachmentId,
                    payload__filename,
                    payload__mimeType,
                    payload__partId,
                    payload__parts,
                    raw,
                    sizeEstimate,
                    snippet
                )
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                """,
                (
                    msg["id"],
                    msg["threadId"],
                    msg["historyId"],
                    msg["internalDate"],
                    json.dumps(msg["labelIds"]),
                    msg["payload"]["body"].get("data", None),
                    msg["payload"]["body"].get("size", None),
                    msg["payload"]["body"].get("attachmentId", None),
                    msg["payload"]["filename"],
                    msg["payload"]["mimeType"],
                    msg["payload"]["partId"],
                    json.dumps(msg["payload"].get("parts", None)),
                    msg.get("raw", None),
                    msg["sizeEstimate"],
                    msg["snippet"],
                ),
            )
            cursor.executemany(
                """
                INSERT INTO headers (
                    message_id,
                    name,
                    value
                )
                VALUES (?,?,?)
                """,
                [
                    (msg["id"], header["name"], header["value"])
                    for header in msg["payload"]["headers"]
                ],
            )
        return

    def scan_remote(self) -> set[str]:
        """
        Scans the remote mailbox and retrieves a set of message IDs.

        Returns:
            A set of message IDs (strings) representing the messages in the remote mailbox.
        """
        limit = 1000
        allIds = set()
        pageToken = None
        counter = Counter("Scanning Gmail Messages: ")
        while True:
            resp = self.gmail_service.get_message_list(
                pageToken=pageToken, maxResults=500
            )
            msgs = resp["messages"]
            for msg in msgs:
                allIds.add(msg["id"])
            counter.next(len(msgs))
            if not resp.get("nextPageToken", None) or (
                limit != 0 and len(allIds) >= limit
            ):
                break
            else:
                pageToken = resp.get("nextPageToken", None)
        counter.writeln("Scanning Complete")
        counter.finish()
        return allIds

    def scan_db(self) -> set[str]:
        """
        Scans the database and returns a set of all message IDs.

        Returns:
            set[str]: A set of all message IDs in the database.
        """
        allIds = set()
        with connect("store.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM messages")
            rows = cursor.fetchall()
            for row in rows:
                allIds.add(row[0])
        return allIds
