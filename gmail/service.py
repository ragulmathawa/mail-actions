from typing import TypedDict
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from requests import HTTPError


class MessagePayloadHeader(TypedDict):
    """
    Represents the header of a Gmail message payload.

    Attributes:
        name (str): The name of the header.
        value (str): The value of the header.
    """

    name: str
    value: str


class MessagePayloadBody(TypedDict):
    """
    Represents the body of a Gmail message payload.

    Attributes:
        data (str): The data of the body.
        size (int): The size of the body.
        attachmentId (str): The attachment ID of the body.
    """

    data: str
    size: int
    attachmentId: str


class MessagePayload(TypedDict):
    """
    Represents the payload of a Gmail message.

    Attributes:
        body (Dict): The body of the message.
        filename (str): The filename of the message.
        headers (List[Dict]): The list of headers of the message.
        mimeType (str): The MIME type of the message.
        partId (str): The part ID of the message.
        parts (List[Dict]): The list of parts of the message.
    """

    body: MessagePayloadBody
    filename: str
    headers: list[MessagePayloadHeader]
    mimeType: str
    partId: str
    parts: list[dict]


class Message(TypedDict):
    """
    Represents a Gmail message.

    Attributes:
        historyId (str): The history ID of the message.
        id (str): The ID of the message.
        internalDate (str): The internal date of the message.
        labelIds (List[str]): The list of label IDs applied to the message.
        payload (Dict): The payload of the message.
        raw (str): The raw content of the message.
        sizeEstimate (int): The estimated size of the message.
        snippet (str): The snippet of the message.
        threadId (str): The ID of the thread the message belongs to.
    """

    historyId: str
    id: str
    internalDate: str
    labelIds: list[str]
    payload: MessagePayload
    raw: str
    sizeEstimate: int
    snippet: str
    threadId: str


class MessageListItem(TypedDict):
    """
    Represents a Gmail message list item.

    Attributes:
        id (str): The ID of the message.
        threadId (str): The ID of the thread the message belongs to.
    """

    id: str
    threadId: str


class Profile(TypedDict):
    """
    Represents the profile of a Gmail user.

    Attributes:
        emailAddress (str): The email address of the user.
        historyId (str): The current history ID of the user's mailbox.
        messagesTotal (int): The total number of messages in the user's mailbox.
        threadsTotal (int): The total number of threads in the user's mailbox.
    """

    emailAddress: str
    historyId: str
    messagesTotal: int
    threadsTotal: int


class MessageList(TypedDict):
    """
    Represents a list of messages retrieved from Gmail.

    Attributes:
        messages (list[MessageListItem]): The list of messages.
        nextPageToken (str): The token for the next page of messages.
        resultSizeEstimate (int): The estimated total number of messages in the result set.
    """

    messages: list[MessageListItem]
    nextPageToken: str
    resultSizeEstimate: int


class GMailService:
    def __init__(self, credentials: Credentials):
        self.credentials = credentials
        self.service = build("gmail", "v1", credentials=self.credentials)

    def get_profile(self) -> Profile:
        """
        Fetches the profile of the user.

        Returns:
            Profile: A Profile object containing the user's profile information.

        Raises:
            Exception: If an HTTP error occurs while fetching the profile.
        """
        profile = self.service.users().getProfile(userId="me")
        try:
            response = profile.execute()
            return response
        except HTTPError as e:
            raise Exception(
                f"Http error with status code {e.response.status_code} occurred while fetching profile, {e.response.content}"
            )

    def get_labels(self) -> dict:
        """
        Fetches the labels for the user.

        Returns:
            dict: A dictionary containing the labels with the following format:
            ```json
            {
                "labels": [
                    {"id": "Label_6", "name": "not imp", "messageListVisibility": "show", "labelListVisibility": "labelShow", "type": "user"},
                    {"id": "SENT", "name": "SENT", "messageListVisibility": "hide", "labelListVisibility": "labelShow", "type": "system"}
                ]
            }
            ```json

        Raises:
            Exception: If an HTTP error occurs while fetching the labels.
        """
        labels = self.service.users().labels().list(userId="me")
        try:
            response = labels.execute()
            return response
        except HTTPError as e:
            raise Exception(
                f"Http error with status code {e.response.status_code} occurred while fetching labels, {e.response.content}"
            )

    def get_message_list(self, maxResults=None, pageToken=None) -> MessageList:
        """
        Fetches the messages for the user.

        Args:
            maxResults (int, optional): The maximum number of messages to retrieve. API Defaults to 100, max allowed is 500.
            pageToken (str, optional): The page token for pagination. Defaults to None(First Page).

        Returns:
            MessageList: A MessageList object containing the list of messages.

        Raises:
            Exception: If an HTTP error occurs while fetching the messages.
        """
        messages = (
            self.service.users()
            .messages()
            .list(userId="me", maxResults=maxResults, pageToken=pageToken)
        )
        try:
            response = messages.execute()
            return response
        except HTTPError as e:
            raise Exception(
                f"Http error with status code {e.response.status_code} occurred while fetching messages, {e.response.content}"
            )

    def get_message(self, messageId: str) -> Message:
        """
        Fetches a message by ID.

        Args:
            messageId (str): The ID of the message to retrieve.

        Returns:
            Message: A Message object containing the message.

        Raises:
            Exception: If an HTTP error occurs while fetching the message.
        """
        message = self.service.users().messages().get(userId="me", id=messageId)
        try:
            response = message.execute()
            return response
        except HTTPError as e:
            raise Exception(
                f"Http error with status code {e.response.status_code} occurred while fetching message, {e.response.content}"
            )

    def close(self):
        """
        Closes the service connection.
        """
        self.service.close()
