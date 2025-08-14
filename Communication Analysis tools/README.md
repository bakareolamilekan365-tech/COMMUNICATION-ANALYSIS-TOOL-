 # Communication Analysis Tool

## Overview
This is a command-line interface (CLI) tool designed to analyze various forms of text-based communication, providing insights into content characteristics and behavioral patterns. It can process email files, WhatsApp chat exports, and custom user-typed messages.

## Features
 - Spam Detection: Classifies messages as 'SPAM' or 'HAM'.
 - Sentiment Analysis: Determines the emotional tone (positive, neutral, negative) of messages.
 - Style Analysis: Assesses the formality and calculates a numerical style score for communication.
 - Behavioral Insights: Analyzes communication patterns to identify top senders, average response times (for conversations), and offers suggestions for improving engagement.
 - Comprehensive Reporting: Generates detailed text reports for analysis results, saved to a data/reports/ directory.
 - CLI Summary: Provides a quick, condensed summary of key metrics directly in the terminal after a report is generated.
 - Flexible Input: Supports various file formats and direct user input.

## Supported Communication Formats
The tool is designed to intelligently parse the following formats:
 - Standard Email Files: Single .txt files containing email headers (From:, Date:, Subject:, Conversation-ID:) followed by the message body.
 - Multi-Email Files: Single .txt files containing multiple standard emails separated by the ---EMAIL_BOUNDARY--- string on its own line.
 - WhatsApp Chat Exports: .txt files exported directly from WhatsApp, following the typical MM/DD/YY, HH:MM AM/PM - Sender: Message format.
 - SMS/Other Generic Text: Custom messages typed directly into the CLI.

## Setup
 - Clone or download: Get the project files.
 - Python Environment: Ensure you have Python 3.8+ installed.
 - Directory Structure:
Make sure your project directory has the following structure:
Group16/
├── main.py                             # Main CLI entry point for the tool
├── train_spam_detector.py             # Script to train a spam detection model
├── test_main.py                       # General test file to run multiple modules (manual or CLI tests)

├── README.md                          # Brief project overview and usage instructions
├── technical_documentation.docx       # Detailed technical insights (architecture, modules, etc.)
├── Communication Analysis Tool - Project Overview.docx   # High-level project vision & objectives
├── Project Requirements.docx          # Functional and non-functional requirements
├── Analysis Tool User Manual.docx     # End-user manual with usage instructions

├── data/                              # Stores all data-related subfolders
│   ├── reports/                       #  Generated reports will be saved here
│   ├── sample_emails/                # Default sample emails for analysis
│   └── training_data/                # Data used for training the spam classifier

├── digitallogsample/                 # Raw log samples from digital conversations
│   ├── ham_messages.txt              # Clean/ham messages sample
│   └── spam_messages.txt             # Spam messages sample

├── modules/                          # Core analysis modules
│   ├── __init__.py                   # Makes 'modules' a Python package
│   ├── data_parser.py                # Parses and structures raw input data
│   ├── spam_detector.py              # Detects spam using trained model
│   ├── sentiment_analyzer.py         # Analyzes sentiment (positive, negative, neutral)
│   ├── style_analyzer.py             # Scores writing style and formality
│   ├── report_generator.py           # Orchestrates overall analysis and report formatting
│   └── metrics_calculator.py         # Calculates summary stats and behavioral metrics

├── tests/                            # Unit tests for each module
│   ├── __init__.py                   # Makes 'tests' a Python package
│   ├── test_data_parser.py           # Tests for `data_parser.py`
│   ├── test_spam_detector.py         # Tests for `spam_detector.py`
│   ├── test_sentiment_analyzer.py    # Tests for `sentiment_analyzer.py`
│   ├── test_style_analyzer.py        # Tests for `style_analyzer.py`
│   ├── test_report_generator.py      # Tests for `report_generator.py`
│   └── test_metrics_calculator.py    # Tests for `metrics_calculator.py`

 - data/training_data/: This directory should contain files necessary for your SpamDetector to train (e.g., ham_messages.txt, spam_messages.txt)
 - data/sample_emails/: This is where you'll place your email and WhatsApp .txt files for analysis


## Usage
Navigate to the your_project_root/ directory in your terminal or command prompt. #in this case which is Group 16
 'cd C:\Users\ABDULL\Desktop\Group 16  #the project's path
 'python main.py'

You will be presented with the main menu:

 'Communication Analysis CLI'
 '1. Run full analysis on sample dataset'
 '2. Analyze a custom text file'
 '3. Type and analyze a custom message'
 '4. Exit'

1. Run full analysis on sample dataset
This option processes all '.txt' files found in the 'data/sample_emails/' directory. It will automatically detect if a file is a single email, a multi-email file, or a WhatsApp chat export.
 -Input: Enter '1'.
 -Output: 'A comprehensive report will be saved to data/reports/' and a summary will be printed to the CLI.

2. Analyze a custom text file
This option allows you to select a specific file from your 'data/sample_emails/' directory or provide a full path to any .txt'' file on your system.
 -Input: Enter '2'.
  You will see a numbered list of available sample files.
  To select a sample file: Enter its corresponding number.
  To enter a path manually: Enter '0', then type the full path to your '.txt' file.
 -Output: A detailed report for the selected file will be saved to data/reports/ and a summary will be printed to the CLI.

3. Type and analyze a custom message
This option allows you to manually type a message and its associated metadata for immediate analysis.
 -Input: Enter '3'.
 -Message Type Selection:
  You will first choose the type of message you're typing:
   'Select Message Type:'
      '1. WhatsApp Chat Message'
      '2. Email Message (with optional headers)'
      '3. SMS Message'
      '4. Other / Generic Text'
      '5. Back to Main Menu'
Choose 1 for WhatsApp, 2 for Email, 3 for SMS, 4 for Other.
Choose 5 to go back to the main menu.
Metadata Input:
 -You will be prompted for a Sender name and Conversation ID. These are optional.
 -To go back to message type selection: Type 'back' at either the sender or conversation ID prompt.

Message Content Input:
 -You will then be prompted to type your message.
 To finish typing: Press [Enter] on an empty line.
 To cancel and go back to message type selection: Type cancel on a new line and press [Enter].
Output: A report for your typed message will be saved to 'data/reports/' and a summary will be printed to the CLI.
Continuous Analysis: After analysis, you will be asked if you want to "Analyze another custom message? (y/n)". Type 'y' to analyze another message of any type, or 'n' to return to the main menu.

4. Exit
Input: Enter '4'.
Output: The CLI will close.

## Reprt Output Details
Reports are saved as '.txt' files in the 'data/reports/' directory. Each report includes:
 - Individual Message Analysis: Detailed breakdown for each parsed message, including source, message ID, subject, sender, conversation ID, timestamp, message body preview, spam status, sentiment, style score, and formality.
 - Summary Metrics: Aggregated statistics like total messages, spam distribution, sentiment breakdown, average style score, and formality distribution.
 - Behavioral Insights: Analysis of communication patterns, including top senders, average response delay (if sufficient data is available within a conversation), and actionable suggestions.

## Customization
 - Lexicons: You can modify the positive_words and negative_words sets in modules/sentiment_analyzer.py to refine sentiment detection for specific contexts.
 - WhatsApp Regex: If your WhatsApp export format differs, you might need to adjust the whatsapp_line_pattern regex in modules/report_generator.py.
 - Email Boundary: The EMAIL_BOUNDARY_SEPARATOR in modules/report_generator.py can be changed if you prefer a different separator for multi-email files.