"""
This is the main command-line interface (CLI) for the Communication Analysis Tool.

It provides a menu-driven system for users to:
1. Run a full analysis on a predefined sample dataset.
2. Analyze a custom text file (either from samples or a user-provided path).
3. Type and analyze a custom message, with options for message type (WhatsApp, Email, SMS, Other),   and flexible input for sender/conversation ID, including "back" and "cancel" options for user control.
4. Exit the application.

The CLI orchestrates calls to various modules in the 'modules/' directory,
primarily 'report_generator.py', to perform the analysis and generate reports.
"""
from modules.spam_detector import SpamDetector
from modules.style_analyzer import StyleAnalyzer
from modules.sentiment_analyzer import SentimentAnalyzer
from modules.report_generator import (
    generate_custom_test_report,
    generate_report,
    generate_report_from_custom_input
)

import os
import time

def list_sample_files(directory="data/sample_emails/"):
    """
    Lists sample files in the specified directory, returning a list of
    (display_name, full_path) tuples.
    """
    try:
        files = os.listdir(directory)
        if not files:
            print(f"[X] No sample files found in '{directory}'.")
            return []

        # Store files with their full relative paths for selection
        sample_file_paths = []
        print("\nAvailable sample files:")
        for i, f in enumerate(files):
            full_path = os.path.join(directory, f)
            sample_file_paths.append((f, full_path)) # Store display name and full path
            print(f" {i + 1}. {f}") # Display with number and just the filename
        return sample_file_paths
    except FileNotFoundError:
        print(f"[X] Sample directory '{directory}' not found.")
        return []

def print_menu():
    print("\nCommunication Analysis CLI")
    print("1. Run full analysis on sample dataset")
    print("2. Analyze a custom text file")
    print("3. Type and analyze a custom message")
    print("4. Exit")

def print_message_type_menu():
    print("\nSelect Message Type:")
    print("  1. WhatsApp Chat Message")
    print("  2. Email Message (with optional headers)")
    print("  3. SMS Message")
    print("  4. Other / Generic Text")
    print("  5. Back to Main Menu")

def main():
    while True:
        print_menu()
        choice = input("Enter your choice (1-4): ").strip()

        if choice == '1':
            print("\n[!] Running full analysis on sample dataset...")
            generate_report("sample_emails")

        elif choice == '2':
            print("\nListing available sample files...")
            available_files = list_sample_files()
            if not available_files:
                print("[X] No files to select from. Please add files to the sample directory or provide a full path.")
                continue

            print(" 0. Enter a custom file path manually")

            file_selection_input = input("\nEnter the number of the file to analyze, or '0' for a custom path: ").strip()

            selected_file_path = None
            try:
                selection_number = int(file_selection_input)
                if selection_number == 0:
                    selected_file_path = input("Please enter the full path to your custom text file: ").strip()
                elif 1 <= selection_number <= len(available_files):
                    selected_file_path = available_files[selection_number - 1][1]
                else:
                    print("[X] Invalid number. Please enter a number from the list or '0'.")
                    continue
            except ValueError:
                selected_file_path = file_selection_input

            if not selected_file_path:
                print("[X] No file path provided.")
                continue
            if not os.path.exists(selected_file_path):
                print(f"[X] File not found at '{selected_file_path}'. Please check the path and try again.")
                continue

            timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
            output_name = f"data/reports/custom_report_{timestamp}.txt"
            generate_custom_test_report(selected_file_path, output_path=output_name)

        elif choice == '3':
            while True: # Loop for selecting message type
                print_message_type_menu()
                type_choice = input("Enter message type choice (1-5): ").strip()
                
                message_type = "Other" # Default type
                if type_choice == '1':
                    message_type = "WhatsApp"
                elif type_choice == '2':
                    message_type = "Email"
                elif type_choice == '3':
                    message_type = "SMS"
                elif type_choice == '4':
                    message_type = "Other"
                elif type_choice == '5':
                    break # Go back to main menu
                else:
                    print("[X] Invalid message type option. Try again.")
                    continue

                print(f"\n--- Analyzing Custom {message_type} Message ---")
                
                # Prompt for sender name with a back option
                sender_input = input("Enter sender name (optional, leave blank for default, type 'back' to change type): ").strip()
                if sender_input.lower() == 'back':
                    print("Going back to message type selection.")
                    continue # Restart the message type loop

                # Prompt for conversation ID with a back option
                convo_id_input = input("Enter conversation ID (optional, leave blank for unique ID, type 'back' to change type): ").strip()
                if convo_id_input.lower() == 'back':
                    print("Going back to message type selection.")
                    continue # Restart the message type loop

                print("\nType or paste your message below.")
                print("Press [Enter] on an empty line to finish input, or type 'cancel' on a new line to go back:")

                lines = []
                while True:
                    line = input()
                    if line.strip().lower() == "cancel": # Check for cancel keyword
                        print("Message input cancelled. Going back to message type selection.")
                        lines = [] # Clear any partial input
                        break # Exit inner input loop
                    if line.strip() == "":
                        break # Finish input
                    lines.append(line)

                user_input = "\n".join(lines).strip()

                if not user_input: # This covers empty input or if 'cancel' was typed
                    if lines: # If 'cancel' was typed, lines list might not be empty, but user_input is empty.
                              # This check ensures we truly cancel if 'cancel' was the last thing.
                        print("[X] No input received or message cancelled.")
                    continue # Go back to message type selection

                # Pass the optional sender, convo ID, and the new message_type
                generate_report_from_custom_input(
                    user_input,
                    sender=sender_input if sender_input else None,
                    conversation_id=convo_id_input if convo_id_input else None,
                    message_type=message_type
                )
                
                # After analysis, give option to analyze another custom message or go back
                another_message = input("\nAnalyze another custom message? (y/n): ").strip().lower()
                if another_message != 'y':
                    break # Go back to main menu

        elif choice == '4':
            print("[!] Exiting CLI. Goodbye!")
            break

        else:
            print("[X] Invalid option. Try again.")

if __name__ == "__main__":
    main()
