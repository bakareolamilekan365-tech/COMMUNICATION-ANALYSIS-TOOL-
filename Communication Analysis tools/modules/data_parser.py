"""
This module contains functions responsible for parsing various communication log formats
(single emails, multi-email files, and WhatsApp chat exports) into a structured
dictionary format for further analysis.
"""

from datetime import datetime
#logic for breaking down data to be readable for python
class Message:
    def __init__(self, sender, recipient, timestamp, subject, body, is_outgoing):
        self.sender = sender  # who sent the message
        self.recipient = recipient  # who received the message
        self.timestamp = timestamp  # Datetime object for when it was sent
        self.subject = subject  # subject line
        self.body = body  # full message content
        self.is_outgoing = is_outgoing  # True if sent by the user

class MessageParser:
    def __init__(self, user_alias=None):
        self.user_alias = user_alias  # Helps flag outgoing messages

    def parse_file(self, filepath):
        messages = []  # final list of parsed Message objects
        current_msg = {}  # Temp dictionary to store one message at a time

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()  # remove leading/trailing whitespace

                    # Parse sender
                    if line.startswith("From:"):
                        current_msg['sender'] = line[5:].strip()
                    # Parse recipient
                    elif line.startswith("To:"):
                        current_msg['recipient'] = line[3:].strip()
                    # Parse date and convert to datetime object
                    elif line.startswith("Date:"):
                        date_str = line[5:].strip()
                        try:
                            current_msg['timestamp'] = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                        except ValueError:
                            current_msg['timestamp'] = datetime.now()  # fallback if date format is wrong
                    # Parse subject
                    elif line.startswith("Subject:"):
                        current_msg['subject'] = line[8:].strip()
                    # Start body section
                    elif line.startswith("Body:"):
                        current_msg['body'] = ""
                    # End of one message, create Message object and add to list
                    elif line == "---":
                        msg = Message(
                            sender=current_msg.get('sender', ''),
                            recipient=current_msg.get('recipient', ''),
                            timestamp=current_msg.get('timestamp', datetime.now()),
                            subject=current_msg.get('subject', ''),
                            body=current_msg.get('body', ''),
                            is_outgoing=(current_msg.get('sender') == self.user_alias)
                        )
                        messages.append(msg)
                        current_msg = {}  # reset for next message
                    # Add lines to body if in body section
                    else:
                        if 'body' in current_msg:
                            current_msg['body'] += line + "\n"
        except FileNotFoundError:
            print(f"X File not found: {filepath}")  # error message
        return messages

# This parser assumes a specific format for the archives.
# The format is expected to have "From:", "To:", "Date:", "Subject:", and "Body:" lines,
# with "---" separating each

class WhatsappLogParser:
    def __init__(self, user_alias=None):
        self.user_alias = user_alias #whether the message is incoming or outgoing
    def parse_file(self, filepath):
        messages = []
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    #pattern: "20/07/2025, 10:04 - Bakare: Messsage text
                    if " - " in line and ":" in line:  # checking if it looks like a whatsapp text
                     try:
                         #spliting timestamp from message
                         timestamp_part, content_part= line.split(" - " , 1)
                         timestamp = datetime.strptime(timestamp_part, "%d/%m/%y, %H:%M")
                         #seperating sender from body
                         sender_part, body = content_part.split(":", 1)
                         sender= sender_part.strip()
                         recipient = self.user_alias if sender != self.user_alias else "Unknown" #determining the recipient
                         msg = Message(
                             sender=sender,
                             recipient=recipient,
                             timestamp=timestamp,
                             subject="",
                             body=body.strip(),
                             is_outgoing=(sender == self.user_alias)
                         )
                         messages.append(msg)
                     except ValueError:
                         continue #skip malformed lines
        except FileNotFoundError:
                             print(f"X File not found: {filepath}")

#format detection function
def get_parser_for_file(filepath, user_alias=None):
    with open(filepath, 'r', encoding='utf-8') as f:
        first_line = f.readline().strip()
        # Check the first line to determine the format
        if first_line.startswith("From:") or first_line.startswith("To:"):
            return MessageParser(user_alias)
        elif "-" in first_line and ":" in first_line and "," in first_line:
            return WhatsappLogParser(user_alias)
        else:
            raise ValueError("Unknown file format")