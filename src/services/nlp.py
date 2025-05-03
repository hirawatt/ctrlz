# Audio processing service
import soundfile as sf
import numpy as np

class AudioProcessor:
    def __init__(self, sample_rate=16000):
        self.sample_rate = sample_rate

    def load_audio(self, file_path):
        data, _ = sf.read(file_path)
        return data

    def segment_audio(self, audio_data, segment_duration=5):
        segment_samples = segment_duration * self.sample_rate
        return [audio_data[i:i + segment_samples] for i in range(0, len(audio_data), segment_samples)]

# Natural language processing
import spacy

class NLPProcessor:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")

    def analyze_text(self, text):
        doc = self.nlp(text)
        return {
            "entities": [(ent.text, ent.label_) for ent in doc.ents],
            "tokens": [token.text for token in doc],
            "sentences": [sent.text for sent in doc.sents]
        }