class TranscriptResponse:
    def __init__(self, transcript: str, confidence: float):
        self.transcript = transcript
        self.confidence = confidence


class TranslationResponse:
    def __init__(self, translated_text: str, source_language: str, target_language: str):
        self.translated_text = translated_text
        self.source_language = source_language
        self.target_language = target_language


class SuggestionResponse:
    def __init__(self, suggestions: list):
        self.suggestions = suggestions


class AssistantResponse:
    def __init__(self, transcript_response: TranscriptResponse, translation_response: TranslationResponse, suggestion_response: SuggestionResponse):
        self.transcript_response = transcript_response
        self.translation_response = translation_response
        self.suggestion_response = suggestion_response