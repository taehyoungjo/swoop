from __future__ import print_function
import pickle
import os.path
import base64

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def get_message_ids(service,userId,filter):

    # response with filter for emails in inbox
    response = service.users().messages().list(
        userId=userId, q=filter).execute()

    # keep message ids
    messages = []

    if 'messages' in response:
        messages.extend(response['messages'])

    # iterate over next pages
    while 'nextPageToken' in response:
        page_token = response['nextPageToken']

        response = service.users().messages().list(
            userId=userId, q=filter, pageToken=page_token).execute()

        messages.extend(response['messages'])

    return messages

def get_message(service, user_id, msg_id):
  """Get a Message with given ID.

  Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    msg_id: The ID of the Message required.

  Returns:
    A Message.
  """
  try:
    message = service.users().messages().get(userId=user_id, id=msg_id, format="raw").execute()

    print('Message snippet: %s' % message['snippet'])

    msg_str = base64.urlsafe_b64decode(message['raw'].encode('ASCII'))

    print(msg_str)

    return message
  except errors.HttpError or error:
    print('An error occurred: %s' % error)

def main():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server()
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)

    message_ids = get_message_ids(service,"me","label:inbox")

    for message_id in message_ids:
        print(message_id["id"])
        message = get_message(service,"me",message_id["id"])
        # print(message)

if __name__ == '__main__':
    main()
