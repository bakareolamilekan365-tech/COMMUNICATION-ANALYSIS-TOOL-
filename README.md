# Communication Analysis Tool — CSC‑202 Group Project (Group 16)

**Course**: Introduction to Computer Programming Lab II (CSC‑202)  
**Department**: Computer Science  
**Submission Date**: August 14, 2025

---

## Project Overview
A **Command-Line Interface (CLI)** tool that analyzes various forms of text-based communication—emails, WhatsApp chat exports, SMS, and custom messages—to deliver insights into content characteristics and behavioral patterns.  

---

##  Main Features
- **Spam Detection**: Classifies messages as `SPAM` or `HAM`.  
- **Sentiment Analysis**: Detects whether messages are positive, neutral, or negative.  
- **Style Analysis**: Scores the formality and calculates a writing style metric.  
- **Behavioral Insights**: Identifies top senders, average response times, and offers suggestions to improve engagement.  
- **Comprehensive Reporting**: Generates detailed text reports saved under `data/reports/`; includes a CLI summary for quick insights.  

---

##  Supported Formats
- **Standard Email Files** (`.txt`)  
- **Multi-Email Files** with `---EMAIL_BOUNDARY---` separators  
- **WhatsApp Chat Exports** (`.txt`) with typical date/time formats  
- **Custom User Input**: Typed directly within the CLI  

---

##  Directory Structure

```
Group16/
├── main.py
├── train_spam_detector.py
├── test_main.py
├── README.md
├── technical_documentation.docx
├── Communication Analysis Tool - Project Overview.docx
├── Project Requirements.docx
├── Analysis Tool User Manual.docx
├── data/
│   ├── reports/
│   ├── sample_emails/
│   └── training_data/
├── digitallogsample/
│   ├── ham_messages.txt
│   └── spam_messages.txt
├── modules/
│   ├── __init__.py
│   ├── data_parser.py
│   ├── spam_detector.py
│   ├── sentiment_analyzer.py
│   ├── style_analyzer.py
│   ├── report_generator.py
│   └── metrics_calculator.py
└── tests/
    ├── __init__.py
    ├── test_data_parser.py
    ├── test_spam_detector.py
    ├── test_sentiment_analyzer.py
    ├── test_style_analyzer.py
    ├── test_report_generator.py
    └── test_metrics_calculator.py
```

---

##  Setup & Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/bakareolamilekan365-tech/COMMUNICATION-ANALYSIS-TOOL-.git
   cd COMMUNICATION-ANALYSIS-TOOL-
   ```
2. Ensure **Python 3.8+** is installed on your machine.
3. No external dependencies are required.

---

##  Usage Guide

Run the main CLI tool:
```bash
python main.py
```

**Menu Options:**
```
'Communication Analysis CLI'
1. Run full analysis on sample dataset
2. Analyze a custom text file
3. Type and analyze a custom message
4. Exit
```
- Option **1** runs analysis on sample `.txt` files under `data/sample_emails/`.
- Option **2** allows file selection or manual file path input.
- Option **3** lets you type a message with metadata (e.g., sender, conversation ID).
- Option **4** exits the tool.

After analysis, the tool:
- Saves a full report under `data/reports/`
- Prints a summary in the CLI interface

---

##  Customization Options
- Modify the word lists (`positive_words`, `negative_words`) in `modules/sentiment_analyzer.py`.
- Adjust `whatsapp_line_pattern` in `modules/report_generator.py` for custom WhatsApp formats.
- Change `EMAIL_BOUNDARY_SEPARATOR` in `modules/report_generator.py` if needed.

---

##  Contributors
- **Group 16** — LAUTECH CSC‑202 members.

---

