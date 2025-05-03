def format_transcript(transcript):
    return transcript.strip().capitalize()

def log_event(event_message):
    import logging
    logging.basicConfig(level=logging.INFO)
    logging.info(event_message)

def validate_input(input_data):
    if not input_data or not isinstance(input_data, str):
        raise ValueError("Input must be a non-empty string.")
    return True

def extract_keywords(text):
    from sklearn.feature_extraction.text import CountVectorizer
    vectorizer = CountVectorizer(stop_words='english')
    X = vectorizer.fit_transform([text])
    return vectorizer.get_feature_names_out()