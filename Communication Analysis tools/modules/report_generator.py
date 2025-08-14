"""
This module is the core orchestrator for the Communication Analysis Tool.
It handles reading various input message formats (single emails, multi-email files,
WhatsApp chat exports, and direct user input), parsing them, and then
coordinating the analysis by other modules (spam_detector, sentiment_analyzer,
style_analyzer). Finally, it compiles the results, calculates aggregate metrics
using metrics_calculator, and generates comprehensive reports both to a file
and as a summary printed to the command-line interface.
"""
import os
import datetime
import re # Import regular expression module for parsing headers

from modules.spam_detector import SpamDetector
from modules.sentiment_analyzer import SentimentAnalyzer
from modules.style_analyzer import StyleAnalyzer
from modules.metrics_calculator import (
    calculate_content_metrics,
    calculate_engagement_metrics
)

# Define the separator for multiple emails within a single file
EMAIL_BOUNDARY_SEPARATOR = "---EMAIL_BOUNDARY---"

# --- Helper functions for parsing different message formats ---

def _parse_single_email_block(email_block_content):
    """
    Parses a single email's content block (headers + body).
    Returns a dictionary of headers and the email body.
    """
    headers = {
        "Sender": "Unknown",
        "Conversation ID": "N/A",
        "Timestamp": None,
        "Subject": "No Subject"
    }
    body = []
    header_end_found = False

    lines = email_block_content.splitlines()
    for line in lines:
        if not header_end_found and line.strip() == "":
            header_end_found = True
            continue

        if not header_end_found:
            line_lower = line.lower()
            if line_lower.startswith("from:"):
                headers["Sender"] = line[len("from:"):].strip()
            elif line_lower.startswith("date:"):
                date_str = line[len("date:"):].strip()
                try:
                    headers["Timestamp"] = datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    headers["Timestamp"] = date_str # Keep as string if parsing fails
            elif line_lower.startswith("conversation-id:"):
                headers["Conversation ID"] = line[len("conversation-id:"):].strip()
            elif line_lower.startswith("subject:"):
                headers["Subject"] = line[len("subject:"):].strip()
        else:
            body.append(line)

    return headers, "\n".join(body).strip()

def _parse_multi_email_file(file_content, filename):
    """
    Parses a file containing multiple emails separated by EMAIL_BOUNDARY_SEPARATOR.
    Returns a list of dictionaries, each representing a single parsed email.
    """
    parsed_emails = []
    # Split the file content by the defined boundary
    email_blocks = file_content.split(EMAIL_BOUNDARY_SEPARATOR)

    for i, block in enumerate(email_blocks):
        block = block.strip()
        if not block:
            continue # Skip empty blocks (e.g., if separator is at start/end or multiple in a row)

        try:
            headers, message_body = _parse_single_email_block(block)
            parsed_emails.append({
                "Source": filename,
                "Message ID": f"{filename}_email_{i+1}", # Unique ID for each email in the file
                "Sender": headers["Sender"],
                "Conversation ID": headers["Conversation ID"],
                "Timestamp": headers["Timestamp"], # Keep as datetime for sorting
                "Subject": headers["Subject"],
                "Message": message_body,
            })
        except Exception as e:
            print(f"[X] Error parsing email block {i+1} in {filename}: {e}")
            parsed_emails.append({
                "Source": filename,
                "Message ID": f"{filename}_email_{i+1}_error",
                "Error": str(e),
                "Message": block[:200] # Store part of the block for context
            })
    return parsed_emails


def _parse_whatsapp_content(file_content, filename):
    """
    Parses WhatsApp chat export content.
    Returns a list of dictionaries, each representing a single chat message.
    """
    messages = []
    whatsapp_line_pattern = re.compile(
        r"^(\d{1,2}/\d{1,2}/\d{2,4}),\s*" # Date (MM/DD/YY or MM/DD/YYYY), comma, optional whitespace
        r"(\d{1,2}:\d{2}(?:\s*(?i:am|pm))?)\s*-\s*" # Time (HH:MM optional AM/PM case-insensitive, with flexible whitespace)
        r"([^:]+?):\s*(.*)$" # Non-greedy sender name up to first colon, colon, optional whitespace, then message
    )
    
    conversation_id = f"whatsapp_chat_{os.path.basename(filename).replace('.', '_')}"

    for line_num, line in enumerate(file_content.splitlines(), 1):
        line = line.strip()
        if not line:
            continue

        match = whatsapp_line_pattern.match(line)
        
        if match:
            date_part, time_part, sender, message_text = match.groups()
            
            timestamp_str = f"{date_part} {time_part.strip()}"
            parsed_timestamp = None
            try:
                parsed_timestamp = datetime.datetime.strptime(timestamp_str, "%m/%d/%y %I:%M %p")
            except ValueError:
                try:
                    parsed_timestamp = datetime.datetime.strptime(timestamp_str, "%m/%d/%Y %I:%M %p")
                except ValueError:
                    try:
                        parsed_timestamp = datetime.datetime.strptime(timestamp_str, "%m/%d/%y %H:%M")
                    except ValueError:
                        try:
                            parsed_timestamp = datetime.datetime.strptime(timestamp_str, "%m/%d/%Y %H:%M")
                        except ValueError:
                            pass # Keep as None if parsing fails

            messages.append({
                "Source": filename,
                "Message ID": f"{filename}_line_{line_num}",
                "Sender": sender.strip(),
                "Conversation ID": conversation_id,
                "Timestamp": parsed_timestamp, # Store as datetime object
                "Subject": "WhatsApp Chat Message", # Default subject for chat messages
                "Message": message_text.strip()
            })
        else:
            if messages:
                messages[-1]["Message"] += "\n" + line
            elif line_num == 1: # This handles the initial system message if it doesn't match
                continue # Skip the first line if it's not a chat message
            else:
                messages.append({
                    "Source": filename,
                    "Message ID": f"{filename}_line_{line_num}_unformatted",
                    "Sender": "Unknown",
                    "Conversation ID": conversation_id,
                    "Timestamp": None,
                    "Subject": "Unformatted Chat Line",
                    "Message": line
                })
    return messages

def _is_whatsapp_format(first_lines):
    """
    Heuristically checks if the file content looks like a WhatsApp export.
    Checks the first few lines for the typical WhatsApp timestamp/sender pattern.
    """
    whatsapp_line_pattern_check = re.compile(
        r"^\d{1,2}/\d{1,2}/\d{2,4},\s*" # Date
        r"\d{1,2}:\d{2}(?:\s*(?i:am|pm))?\s*-\s*" # Time
        r"[^:]+?:\s*.*$" # Sender and start of message
    )
    for line in first_lines:
        if whatsapp_line_pattern_check.match(line.strip()):
            return True
    return False

def _has_email_boundary(file_content):
    """Checks if the file content contains the multi-email boundary separator."""
    return EMAIL_BOUNDARY_SEPARATOR in file_content

# --- Common function to print summary to CLI ---
def _print_summary_to_cli(summary, behavior):
    """Prints a condensed summary of metrics and insights to the console."""
    print("\n" + "="*30)
    print("  Analysis Summary (CLI)  ")
    print("="*30)

    print("\n--- Summary Metrics ---")
    print(f"Total Messages        : {summary['Total Messages']}")
    print(f"Spam Breakdown        : SPAM = {summary['Spam Counts']['SPAM']}, HAM = {summary['Spam Counts']['HAM']}")
    print(f"Sentiment Breakdown   : {summary['Sentiment Counts']}")
    print(f"Average Style Score   : {summary['Average Style Score']}")
    print(f"Formality Breakdown   : {summary['Formality Counts']}")

    print("\n--- Behavioral Insights ---")
    print(f"Top Senders           : {behavior['Top Senders']}")
    if behavior.get("Average Response time (sec)") is not None:
        print(f"Avg Response Delay    : {behavior['Average Response time (sec)']} seconds")
    else:
        print("Avg Response Delay    : [Not enough data for response time calculation]")

    print("Suggestions           :")
    if behavior["Suggestions"]:
        for tip in behavior["Suggestions"]:
            print(f" - {tip}")
    else:
        print(" - No behavioral recommendations found.")
    print("="*30 + "\n")


# --- Main report generation functions ---

def generate_report(source="sample_emails"):
    # Set path
    input_items = []
    if source == "digitallogssample":
        input_items = [
            ("digitallogssample/ham_messages.txt", "HAM"),
            ("digitallogssample/spam_messages.txt", "SPAM")
        ]
    elif source == "sample_emails":
        input_dir = "data/sample_emails"
        if not os.path.exists(input_dir):
            print(f"[X] Sample emails directory not found: {input_dir}")
            return
        for filename in os.listdir(input_dir):
            if filename.endswith(".txt"):
                input_items.append(os.path.join(input_dir, filename))
    else:
        print(f"[x] Unknown source: {source}")
        return

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_path = f"data/reports/report_{timestamp}.txt"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Initializing modules
    spam_detector = SpamDetector("data/training_data/")
    sentiment_analyzer = SentimentAnalyzer()
    style_analyzer = StyleAnalyzer()

    results = [] # This will store dictionaries for each *message*

    for file_path in input_items:
        if isinstance(file_path, tuple): # For digitallogssample format
            path_to_open = file_path[0]
            try:
                with open(path_to_open, 'r', encoding='utf-8') as f:
                    for line_num, line in enumerate(f, 1):
                        message_body = line.strip()
                        if not message_body: continue

                        spam_status = "SPAM" if spam_detector.predict(message_body) else "HAM"
                        sentiment = sentiment_analyzer.analyze(message_body)
                        style = style_analyzer.analyze(message_body)

                        results.append({
                            "Source": os.path.basename(path_to_open),
                            "Message ID": f"{os.path.basename(path_to_open)}_line_{line_num}",
                            "Message": message_body,
                            "Spam": spam_status,
                            "Sentiment": sentiment,
                            "Style Score": style["Style Score"],
                            "Formality": style["Formality"],
                            "Sender": "Unknown", # Default for these files
                            "Conversation ID": "N/A", # Default
                            "Timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") # Default to current time
                        })
            except Exception as e:
                print(f"[X] Error processing file {os.path.basename(path_to_open)}: {e}")
                results.append({
                    "Source": os.path.basename(path_to_open),
                    "Error": str(e),
                    "Message": "Could not read file."
                })
        else: # For sample_emails directory (which might contain emails or WhatsApp or multi-emails)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    full_content = f.read()

                first_few_lines = full_content.splitlines()[:5] # Check first few lines for format
                
                parsed_messages = []
                if _is_whatsapp_format(first_few_lines):
                    print(f"[!] Detected WhatsApp format for {os.path.basename(file_path)}.")
                    parsed_messages = _parse_whatsapp_content(full_content, os.path.basename(file_path))
                elif _has_email_boundary(full_content): # Check for multi-email boundary
                    print(f"[!] Detected multi-email format for {os.path.basename(file_path)}.")
                    parsed_messages = _parse_multi_email_file(full_content, os.path.basename(file_path))
                else:
                    # Assume single standard email format if not WhatsApp or multi-email
                    headers, message_body = _parse_single_email_block(full_content)
                    parsed_messages.append({
                        "Source": os.path.basename(file_path),
                        "Message ID": f"{os.path.basename(file_path)}_msg",
                        "Sender": headers["Sender"],
                        "Conversation ID": headers["Conversation ID"],
                        "Timestamp": headers["Timestamp"], # Keep as datetime for sorting
                        "Subject": headers["Subject"],
                        "Message": message_body,
                    })

                for msg_data in parsed_messages:
                    message_to_analyze = msg_data.get("Message", "")
                    if not message_to_analyze.strip(): # Skip empty messages
                        continue

                    spam_status = "SPAM" if spam_detector.predict(message_to_analyze) else "HAM"
                    sentiment = sentiment_analyzer.analyze(message_to_analyze)
                    style = style_analyzer.analyze(message_to_analyze)

                    # Update the message data with analysis results
                    msg_data.update({
                        "Spam": spam_status,
                        "Sentiment": sentiment,
                        "Style Score": style["Style Score"],
                        "Formality": style["Formality"]
                    })
                    results.append(msg_data)

            except Exception as e:
                print(f"[X] Error processing file {os.path.basename(file_path)}: {e}")
                results.append({
                    "Source": os.path.basename(file_path),
                    "Error": str(e),
                    "Message": full_content # Store full content for error context
                })

    # Convert datetime objects to string format for metrics_calculator if needed
    for entry in results:
        if isinstance(entry.get("Timestamp"), datetime.datetime):
            entry["Timestamp"] = entry["Timestamp"].strftime("%Y-%m-%d %H:%M:%S")

    # Run metrics after message parsing
    summary = calculate_content_metrics(results)
    behavior = calculate_engagement_metrics(results)

    # Write full analysis report
    with open(output_path, 'w', encoding='utf-8') as out:
        out.write("Communication Analysis Report\n\n")
        out.write("--- Individual Message Analysis ---\n\n")
        for entry in results:
            out.write(f"File: {entry.get('Source', '[unknown]')}\n")
            if "Error" in entry:
                out.write(f" Error: {entry['Error']}\n")
                out.write(f" Original Content: {entry.get('Message', '')[:200]}...\n")
            else:
                out.write(f" Subject: {entry.get('Subject', 'N/A')}\n")
                out.write(f" Sender: {entry.get('Sender', 'N/A')}\n")
                out.write(f" Conversation ID: {entry.get('Conversation ID', 'N/A')}\n")
                out.write(f" Timestamp: {entry.get('Timestamp', 'N/A')}\n")
                out.write(f" Message Body Preview: {entry['Message'][:100]}...\n")
                out.write(f"   Spam      : {entry['Spam']}\n")
                out.write(f"   Sentiment : {entry['Sentiment']}\n")
                out.write(f"   Style     : {entry['Style Score']} ({entry['Formality']})\n")
            out.write("-" * 50 + "\n")

        # Append Summary Metrics
        out.write("\n--- Summary Metrics ---\n\n")
        out.write(f"Total Messages        : {summary['Total Messages']}\n")
        out.write(f"Spam Breakdown        : SPAM = {summary['Spam Counts']['SPAM']}, HAM = {summary['Spam Counts']['HAM']}\n")
        out.write(f"Sentiment Breakdown   : {summary['Sentiment Counts']}\n")
        out.write(f"Average Style Score   : {summary['Average Style Score']}\n")
        out.write(f"Formality Breakdown   : {summary['Formality Counts']}\n")

        # Append Behavioral Insights
        out.write("\n--- Behavioral Insights ---\n\n")
        out.write(f"Top Senders           : {behavior['Top Senders']}\n")
        if behavior.get("Average Response time (sec)") is not None:
            out.write(f"Avg Response Delay    : {behavior['Average Response time (sec)']} seconds\n")
        else:
            out.write("Avg Response Delay    : [Not enough data for response time calculation]\n")
        out.write("Suggestions           :\n")
        if behavior["Suggestions"]:
            for tip in behavior["Suggestions"]:
                out.write(f" - {tip}\n")
        else:
            out.write(" - No behavioral recommendations found.\n")

    print(f"[] Report saved to: {output_path}")
    _print_summary_to_cli(summary, behavior) # Call the new function to print to CLI

# Added message_type parameter with a default
def generate_custom_test_report(
    file_path,
    output_path="data/reports/test_analysis_report.txt",
    spam_detector=None,
    sentiment_analyzer=None,
    style_analyzer=None
):
    # Initialize analyzers
    spam_detector = spam_detector or SpamDetector("data/training_data/")
    sentiment_analyzer = sentiment_analyzer or SentimentAnalyzer()
    style_analyzer = style_analyzer or StyleAnalyzer()

    results = []

    if not os.path.exists(file_path):
        print(f"[X] Input file not found: {file_path}")
        return

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            full_content = f.read()

        first_few_lines = full_content.splitlines()[:5]
        
        parsed_messages = []
        if _is_whatsapp_format(first_few_lines):
            print(f"[!] Detected WhatsApp format for {os.path.basename(file_path)}.")
            parsed_messages = _parse_whatsapp_content(full_content, os.path.basename(file_path))
        elif _has_email_boundary(full_content): # Check for multi-email boundary
            print(f"[!] Detected multi-email format for {os.path.basename(file_path)}.")
            parsed_messages = _parse_multi_email_file(full_content, os.path.basename(file_path))
        else:
            # Assume single standard email format if not WhatsApp or multi-email
            headers, message_body = _parse_single_email_block(full_content)
            parsed_messages.append({
                "Source": os.path.basename(file_path),
                "Message ID": f"{os.path.basename(file_path)}_msg",
                "Sender": headers["Sender"],
                "Conversation ID": headers["Conversation ID"],
                "Timestamp": headers["Timestamp"],
                "Subject": headers["Subject"],
                "Message": message_body,
            })

        for msg_data in parsed_messages:
            message_to_analyze = msg_data.get("Message", "")
            if not message_to_analyze.strip():
                continue

            spam_status = "SPAM" if spam_detector.predict(message_to_analyze) else "HAM"
            sentiment = sentiment_analyzer.analyze(message_to_analyze)
            style = style_analyzer.analyze(message_to_analyze)

            msg_data.update({
                "Spam": spam_status,
                "Sentiment": sentiment,
                "Style Score": style["Style Score"],
                "Formality": style["Formality"]
            })
            results.append(msg_data)

    except Exception as e:
        print(f"[X] Error analyzing file {os.path.basename(file_path)}: {e}")
        results.append({
            "Source": os.path.basename(file_path),
            "Error": str(e),
            "Message": full_content
        })

    # Convert datetime objects to string format for metrics_calculator if needed
    for entry in results:
        if isinstance(entry.get("Timestamp"), datetime.datetime):
            entry["Timestamp"] = entry["Timestamp"].strftime("%Y-%m-%d %H:%M:%S")

    # Run Metrics
    summary = calculate_content_metrics(results)
    behavior = calculate_engagement_metrics(results)

    # Write Full Report
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as out:
        out.write("Custom Test Report\n\n")
        out.write("--- Individual Message Analysis ---\n\n")
        for entry in results:
            out.write(f"File: {entry.get('Source', '[unknown]')}\n")
            if "Error" in entry:
                out.write(f" Error: {entry['Error']}\n")
                out.write(f" Original Content: {entry.get('Message', '')[:200]}...\n")
            else:
                out.write(f" Subject: {entry.get('Subject', 'N/A')}\n")
                out.write(f" Sender: {entry.get('Sender', 'N/A')}\n")
                out.write(f" Conversation ID: {entry.get('Conversation ID', 'N/A')}\n")
                out.write(f" Timestamp: {entry.get('Timestamp', 'N/A')}\n")
                out.write(f" Message Body Preview: {entry['Message'][:100]}...\n")
                out.write(f" Spam: {entry['Spam']}\n")
                out.write(f" Sentiment: {entry['Sentiment']}\n")
                out.write(f" Style: {entry['Style Score']} ({entry['Formality']})\n")
            out.write("-" * 50 + "\n")

        out.write("\n--- Summary Metrics ---\n\n")
        out.write(f"Total Messages        : {summary['Total Messages']}\n")
        out.write(f"Spam Breakdown        : SPAM = {summary['Spam Counts']['SPAM']}, HAM = {summary['Spam Counts']['HAM']}\n")
        out.write(f"Sentiment Breakdown   : {summary['Sentiment Counts']}\n")
        out.write(f"Average Style Score   : {summary['Average Style Score']}\n")
        out.write(f"Formality Breakdown   : {summary['Formality Counts']}\n")

        out.write("\n--- Behavioral Insights ---\n\n")
        out.write(f"Top Senders           : {behavior['Top Senders']}\n")
        if behavior.get("Average Response time (sec)") is not None:
            out.write(f"Avg Response Delay    : {behavior['Average Response time (sec)']} seconds\n")
        else:
            out.write("Avg Response Delay    : [Not enough data for response time calculation]\n")

        out.write("Suggestions           :\n")
        if behavior["Suggestions"]:
            for tip in behavior["Suggestions"]:
                out.write(f" - {tip}\n")
        else:
            out.write(" - No behavioral recommendations found.\n")

    print(f" Custom test report saved to: {output_path}")
    _print_summary_to_cli(summary, behavior) # Call the new function to print to CLI

# Modified to accept message_type parameter
def generate_report_from_custom_input(message, sender=None, conversation_id=None, message_type="Other"):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_path = f"data/reports/report_{timestamp}.txt"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    spam_detector = SpamDetector("data/training_data/")
    sentiment_analyzer = SentimentAnalyzer()
    style_analyzer = StyleAnalyzer()

    results = [] # Prepare a list to hold the single result for consistency

    # Determine metadata based on message_type and user input
    final_sender = sender
    final_convo_id = conversation_id
    final_subject = "Custom Message"
    current_timestamp = datetime.datetime.now()
    parsed_message_content = message # Default to raw message

    if message_type == "WhatsApp":
        # Attempt to parse as a single WhatsApp line
        # We'll create a dummy file content for _parse_whatsapp_content
        dummy_filename = "typed_whatsapp_msg.txt"
        # The parser expects a file-like structure, so we simulate it.
        # It will return a list, we take the first item if successful.
        temp_parsed = _parse_whatsapp_content(message, dummy_filename)
        if temp_parsed:
            parsed_data = temp_parsed[0] # Take the first parsed message
            final_sender = parsed_data.get("Sender", sender if sender else "WhatsApp User")
            final_convo_id = parsed_data.get("Conversation ID", conversation_id if conversation_id else f"typed_whatsapp_convo_{timestamp}")
            current_timestamp = parsed_data.get("Timestamp", current_timestamp)
            final_subject = parsed_data.get("Subject", "WhatsApp Chat Message")
            parsed_message_content = parsed_data.get("Message", message) # Use parsed body
            print(f"[!] Parsed as WhatsApp: Sender='{final_sender}', Convo ID='{final_convo_id}'")
        else:
            print("[X] Could not parse as WhatsApp format. Using generic defaults.")
            final_sender = sender if sender else "WhatsApp User"
            final_convo_id = conversation_id if conversation_id else f"typed_whatsapp_convo_{timestamp}"
            final_subject = "WhatsApp Message (Unparsed)"

    elif message_type == "Email":
        # Attempt to parse as a single email block
        temp_headers, temp_body = _parse_single_email_block(message)
        if temp_headers.get("Sender") != "Unknown" or temp_headers.get("Subject") != "No Subject":
            final_sender = temp_headers.get("Sender", sender if sender else "Email Sender")
            final_convo_id = temp_headers.get("Conversation ID", conversation_id if conversation_id else f"typed_email_convo_{timestamp}")
            current_timestamp = temp_headers.get("Timestamp", current_timestamp)
            final_subject = temp_headers.get("Subject", "Email Message")
            parsed_message_content = temp_body # Use parsed body
            print(f"[!] Parsed as Email: Sender='{final_sender}', Subject='{final_subject}'")
        else:
            print("[X] Could not parse as Email format. Using generic defaults.")
            final_sender = sender if sender else "Email Sender"
            final_convo_id = conversation_id if conversation_id else f"typed_email_convo_{timestamp}"
            final_subject = "Email Message (Unparsed)"

    elif message_type == "SMS":
        final_sender = sender if sender else "SMS Sender"
        final_convo_id = conversation_id if conversation_id else f"typed_sms_convo_{timestamp}"
        final_subject = "SMS Message"
    else: # "Other" or fallback
        final_sender = sender if sender else "User Input"
        final_convo_id = conversation_id if conversation_id else f"manual_convo_{timestamp}"
        final_subject = "Custom Message"

    try:
        spam_status = "SPAM" if spam_detector.predict(parsed_message_content) else "HAM"
        sentiment = sentiment_analyzer.analyze(parsed_message_content)
        style = style_analyzer.analyze(parsed_message_content)

        result = {
            "Source": f"manual_input_{message_type.lower()}",
            "Message ID": "manual_msg_1", # Still 1 message per analysis session
            "Sender": final_sender,
            "Conversation ID": final_convo_id,
            "Timestamp": current_timestamp.strftime("%Y-%m-%d %H:%M:%S") if isinstance(current_timestamp, datetime.datetime) else current_timestamp,
            "Subject": final_subject,
            "Message": parsed_message_content,
            "Spam": spam_status,
            "Sentiment": sentiment,
            "Style Score": style["Style Score"],
            "Formality": style["Formality"]
        }
        results.append(result)

        # Run metrics even for single message, though behavioral will be limited
        summary = calculate_content_metrics(results)
        behavior = calculate_engagement_metrics(results)

        with open(output_path, 'w', encoding='utf-8') as out:
            out.write(f"Single {message_type} Message Analysis Report\n\n")
            out.write("--- Individual Message Analysis ---\n\n")
            out.write(f" Source: {result['Source']}\n")
            out.write(f" Subject: {result['Subject']}\n")
            out.write(f" Sender: {result['Sender']}\n")
            out.write(f" Conversation ID: {result['Conversation ID']}\n")
            out.write(f" Timestamp: {result['Timestamp']}\n")
            out.write(f" Message Body: {result['Message']}\n")
            out.write(f" Spam: {result['Spam']}\n")
            out.write(f" Sentiment: {result['Sentiment']}\n")
            out.write(f" Style: {result['Style Score']} ({result['Formality']})\n")
            out.write("-" * 50 + "\n")

            out.write("\n--- Summary Metrics ---\n\n")
            out.write(f"Total Messages        : {summary['Total Messages']}\n")
            out.write(f"Spam Breakdown        : SPAM = {summary['Spam Counts']['SPAM']}, HAM = {summary['Spam Counts']['HAM']}\n")
            out.write(f"Sentiment Breakdown   : {summary['Sentiment Counts']}\n")
            out.write(f"Average Style Score   : {summary['Average Style Score']}\n")
            out.write(f"Formality Breakdown   : {summary['Formality Counts']}\n")

            out.write("\n--- Behavioral Insights (Limited for single message) ---\n\n")
            out.write(f"Top Senders           : {behavior['Top Senders']}\n")
            if behavior.get("Average Response time (sec)") is not None:
                out.write(f"Avg Response Delay    : {behavior['Average Response time (sec)']} seconds\n")
            else:
                out.write("Avg Response Delay    : [Not enough data for response time calculation]\n")

            out.write("Suggestions           :\n")
            if behavior["Suggestions"]:
                for tip in behavior["Suggestions"]:
                    out.write(f" - {tip}\n")
            else:
                out.write(" - No behavioral recommendations found.\n")

        print(f" Manual input report saved to: {output_path}")
        _print_summary_to_cli(summary, behavior) # Call the new function to print to CLI

    except Exception as e:
        print(f"[X] Error analyzing message: {e}")
