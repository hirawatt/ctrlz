import sounddevice as sd
import numpy as np
import queue
import threading
import time

class MicrophoneCapture:
    def __init__(self, device=None, sample_rate=16000, chunk_size=1024):
        self.device = device
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.stream = None
        self.audio_queue = queue.Queue(maxsize=20)
        self.running = False
        self._lock = threading.Lock()
        self.overflow_count = 0
        self.last_overflow_report = 0
        self.gain_factor = 1.0
        self.level_history = []

    def get_device_list(self):
        device_list = []
        try:
            devices = sd.query_devices()
            for i, device in enumerate(devices):
                if device['max_input_channels'] > 0:
                    device_list.append(f"{i}: {device['name']}")
        except Exception as e:
            print(f"Error listing devices: {e}")
        return device_list

    def find_supported_rate(self, device_id=None):
        preferred_rates = [16000, 22050, 44100, 48000]
        try:
            device_info = sd.query_devices(device_id)
            default_rate = int(device_info['default_samplerate'])
            for rate in preferred_rates:
                try:
                    sd.check_input_settings(device=device_id, samplerate=rate)
                    return rate
                except:
                    continue
            return default_rate
        except:
            return 16000

    def start_stream(self, device_index=None):
        if device_index is not None:
            self.device = device_index
        self.sample_rate = 16000
        print(f"Initializing audio stream at {self.sample_rate} Hz")
        
        with self._lock:
            if self.stream is not None:
                return
            try:
                self.stream = sd.InputStream(
                    device=self.device,
                    samplerate=self.sample_rate,
                    channels=1,
                    dtype='int16',
                    blocksize=self.chunk_size,
                    callback=self._audio_callback,
                    latency='low'
                )
                self.running = True
                self.stream.start()
                print(f"Audio stream started (device={self.device}, chunk_size={self.chunk_size})")
                return self.stream
            except Exception as e:
                print(f"Error starting stream: {e}")
                self._try_fallback_device()

    def _try_fallback_device(self):
        print("Trying default device...")
        self.device = None
        self.sample_rate = self.find_supported_rate(None)
        self.stream = sd.InputStream(
            channels=1,
            samplerate=self.sample_rate,
            dtype='int16',
            blocksize=self.chunk_size,
            callback=self._audio_callback,
            latency='low'
        )
        self.running = True
        self.stream.start()
        print("Fallback stream started with default device")
        return self.stream

    def _audio_callback(self, indata, frames, time_info, status):
        if status and status.input_overflow:
            current_time = time.time()
            self.overflow_count += 1
            if current_time - self.last_overflow_report > 5:
                print(f"Audio input overflow occurred {self.overflow_count} times in the last 5 seconds")
                self.overflow_count = 0
                self.last_overflow_report = current_time
                if self.chunk_size > 512:
                    self.chunk_size //= 2
                    print(f"Reducing chunk size to {self.chunk_size}")
        
        audio_data = np.squeeze(indata.copy())
        audio_level = np.abs(audio_data).mean()
        
        self.level_history.append(audio_level)
        if len(self.level_history) > 50:
            self.level_history.pop(0)
        
        avg_level = np.mean(self.level_history)
        
        target_gain = 1.0
        if avg_level > 0 and avg_level < 100:
            target_gain = min(10, 150 / (avg_level + 1e-6))
            
            if abs(target_gain - self.gain_factor) > 0.5:
                print(f"Adjusting gain: level={avg_level:.2f}, gain={target_gain:.1f}x")
            
            self.gain_factor = self.gain_factor * 0.95 + target_gain * 0.05
            audio_data = np.clip(audio_data * self.gain_factor, -32767, 32767).astype(np.int16)
        
        if audio_level > 100 and time.time() % 2 < 0.1:
            print(f"Audio level: {audio_level:.1f}")
        
        try:
            if not self.audio_queue.full():
                self.audio_queue.put_nowait(audio_data)
        except queue.Full:
            try:
                self.audio_queue.get_nowait()
                self.audio_queue.put_nowait(audio_data)
            except:
                pass

    def get_audio_chunk(self, timeout=0.2):
        try:
            return self.audio_queue.get(timeout=timeout)
        except queue.Empty:
            return np.zeros(self.chunk_size, dtype=np.int16)

    def get_sample_rate(self):
        return self.sample_rate

    def close(self):
        with self._lock:
            self.running = False
            if self.stream:
                try:
                    self.stream.stop()
                    self.stream.close()
                except Exception as e:
                    print(f"Error closing stream: {e}")
                self.stream = None
            
        try:
            while not self.audio_queue.empty():
                self.audio_queue.get_nowait()
        except:
            pass
