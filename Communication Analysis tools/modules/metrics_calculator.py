""""
metrics_calculator.py
Calculates summary metrics from analyzed messages , including:
- Spam distribution
- Sentiment breakdown
- Style score average
- Formality scores
Accepts results lst from repor_generator and returns a summary dictionary.
"""
from collections import defaultdict
from datetime import datetime

def calculate_content_metrics(results):
    #initialize counters and containers
    total = 0 #total number of successfully analyzed messages
    spam_counts = {"SPAM":0, "HAM":0} #Tracks spam/ham predictions
    sentiment_counts = {"positive":0, "neutral":0, "negative":0} #sentiment distribution
    style_scores = [] #collects all style scores to calculate average
    formality_counts = {"formal":0 , "informal":0, "neutral":0} #tracks formality tags, added neutral

    #loop through each analyzed message in the results list
    for entry in results:
        if "Error" in entry:
            continue #skip entries that had processing errors
        total += 1 #count valid messages

        #count SPAM/HAM predictions
        spam_value = entry.get("Spam")
        if spam_value in spam_counts:
            spam_counts[spam_value] += 1

        #Count sentiment labels
        sentiment_value = entry.get("Sentiment")
        if sentiment_value in sentiment_counts:
            sentiment_counts[sentiment_value] += 1

        #Collect style scores for averaging
        style_score = entry.get("Style Score")
        if isinstance(style_score,(int,float)):
            style_scores.append(style_score)

        # Count formality labels
        formality = entry.get("Formality")
        # Ensure formality value is lowercase before checking against counts
        if formality and formality.lower() in formality_counts:
            formality_counts[formality.lower()] += 1

    #Calculate average style score (rounded to 2 decimals), or 0.0 if no scores found
    avg_style_score = round(sum(style_scores)/ len(style_scores),2) if style_scores else 0.0

    #return all metrics as a dictionary to be included in the report
    return{
        "Total Messages": total,
        "Spam Counts": spam_counts,
        "Sentiment Counts": sentiment_counts,
        "Average Style Score": avg_style_score,
        "Formality Counts": formality_counts
    }

def calculate_engagement_metrics(results):
    sender_freq= defaultdict(int)
    conversations_times = defaultdict(list)
    response_gaps = []
    formality_counts = {"formal":0 , "informal":0, "neutral":0} # Ensure neutral is included
    style_scores = [] # Collect style scores for average within behavioral insights context

    for entry in results:
        if "Error" in entry:
            continue
        sender = entry.get("Sender")
        if sender:
            sender_freq[sender] +=1
        
        style_score = entry.get("Style Score")
        if isinstance(style_score,(int,float)):
            style_scores.append(style_score)
        
        formality = entry.get("Formality")
        if formality and formality.lower() in formality_counts:
            formality_counts[formality.lower()] += 1

        convo_id = entry.get("Conversation ID")
        timestamp = entry.get("Timestamp")
        
        if convo_id and timestamp:
            try:
                # Ensure timestamp is a datetime object or convert it
                if isinstance(timestamp, datetime):
                    time_obj = timestamp
                elif isinstance(timestamp, str):
                    # Attempt to parse common formats. Add more if needed.
                    try:
                        time_obj = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        # Try WhatsApp format if email format fails
                        try: 
                            time_obj = datetime.strptime(timestamp, "%m/%d/%y %I:%M %p")
                        except ValueError:
                            try:
                                time_obj = datetime.strptime(timestamp, "%m/%d/%Y %I:%M %p")
                            except ValueError:
                                try:
                                    time_obj = datetime.strptime(timestamp, "%m/%d/%y %H:%M")
                                except ValueError:
                                    try:
                                        time_obj = datetime.strptime(timestamp, "%m/%d/%Y %H:%M")
                                    except ValueError:
                                        time_obj = None # If all parsing fails
                else:
                    time_obj = None # Not a datetime or string

                if time_obj:
                    conversations_times[convo_id].append(time_obj)
            except Exception: # Catch any parsing errors that might slip through
                pass # Continue processing other entries

    for times in conversations_times.values():
        if len(times) >= 2:
            times.sort() # Ensure timestamps are sorted chronologically
            for i in range(1, len(times)):
                gap = (times[i] - times[i - 1]).total_seconds()
                response_gaps.append(gap)
    
    avg_response_time = round(sum(response_gaps)/len(response_gaps),2) if response_gaps else None
    # Calculate average style score from collected style_scores for behavioral context
    avg_style_score = round(sum(style_scores)/len(style_scores),2) if style_scores else 0.0

    suggestions=[]
    
    # Suggestion 1: Improve clarity/structure based on average style score
    if avg_style_score < 40: # Lower threshold for "Improve clarity"
        suggestions.append("Improve clarity and structure in messages.")
    
    # Suggestion 2: Use more formal phrasing
    # Only suggest if informal count is significantly higher than formal, and there are non-neutral messages
    total_non_neutral_formality = formality_counts["formal"] + formality_counts["informal"]
    if total_non_neutral_formality > 0 and formality_counts["informal"] > formality_counts["formal"] * 1.5: # Informal is 1.5x more than formal
        suggestions.append("Consider using more formal phrasing for professional contexts.")
    
    # Suggestion 3: Respond more promptly
    # Adjusted threshold for "promptly" (e.g., > 1 hour = 3600 seconds)
    if avg_response_time is not None and avg_response_time > 3600:
        suggestions.append("Respond to messages more promptly to improve conversation engagement.")

    return{
        "Top Senders": dict(sender_freq),
        "Average Response time (sec)":avg_response_time,
        "Suggestions": suggestions,
        "Formality Counts": formality_counts # Included for completeness in behavioral report
    }
