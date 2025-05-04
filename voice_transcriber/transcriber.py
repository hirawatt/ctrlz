from faster_whisper import WhisperModel
import numpy as np
import queue
import threading
import time
from config import MODEL_SIZE, SAMPLE_RATE

class RealtimeTranscriber:
    def __init__(self, model_size=MODEL_SIZE, sample_rate=SAMPLE_RATE):
        print(f"Initializing transcriber with model size: {model_size}, sample rate: {sample_rate}")
        self.model = WhisperModel(model_size, device="cpu", compute_type="int8")
        self.audio_queue = queue.Queue()
        self.text_queue = queue.Queue()
        self.running = False
        self.sample_rate = sample_rate
        self.buffer = np.array([], dtype=np.float32)
        self.min_audio_length = 0.5
        
    def start(self):
        print("Starting transcriber thread")
        self.running = True
        self.thread = threading.Thread(target=self._process_audio)
        self.thread.daemon = True
        self.thread.start()
        
    def stop(self):
        print("Stopping transcriber")
        self.running = False
        if hasattr(self, 'thread'):
            self.thread.join(timeout=2.0)
            
    def add_audio(self, audio_chunk):
        if audio_chunk.dtype == np.int16:
            audio_chunk = audio_chunk.astype(np.float32) / 32768.0
        
        if np.abs(audio_chunk).mean() > 0.001:
            self.audio_queue.put(audio_chunk)
        
    def get_transcription(self):
        if not self.text_queue.empty():
            return self.text_queue.get()
        return None
        
    def _process_audio(self):
        print("Audio processing thread started")
        
        while self.running:
            while not self.audio_queue.empty():
                chunk = self.audio_queue.get()
                self.buffer = np.append(self.buffer, chunk)
            
            buffer_duration = len(self.buffer) / self.sample_rate
            if buffer_duration >= self.min_audio_length:
                try:
                    segments, _ = self.model.transcribe(
                        self.buffer, 
                        beam_size=5,
                        language="en",
                        vad_filter=True,
                        vad_parameters=dict(min_silence_duration_ms=500)
                    )
                    
                    text = ""
                    for segment in segments:
                        text += segment.text
                    
                    if text.strip():
                        self.text_queue.put(text.strip())
                        print(f"Transcribed: '{text.strip()}'")
                    
                    keep_duration = 0.5
                    if buffer_duration > keep_duration:
                        self.buffer = self.buffer[-int(keep_duration * self.sample_rate):]
                    
                except Exception as e:
                    print(f"Error during transcription: {e}")
            
            time.sleep(0.1)

def simple_test():
    from mic_capture import MicrophoneCapture
    
    transcriber = RealtimeTranscriber()
    transcriber.start()
    
    mic = MicrophoneCapture()
    mic.start_stream()
    
    try:
        print("Speak into your microphone for 10 seconds...")
        for _ in range(100):
            audio_chunk = mic.get_audio_chunk()
            transcriber.add_audio(audio_chunk)
            
            text = transcriber.get_transcription()
            if text:
                print(f"Transcription: {text}")
            
            time.sleep(0.1)
    finally:
        mic.close()
        transcriber.stop()

if __name__ == "__main__":
    simple_test()