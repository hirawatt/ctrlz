"""Module for capturing audio from phone calls using raw sockets."""

import socket
import base64
import threading
import json
import numpy as np
from config import SOCKET_HOST, SOCKET_PORT

class PhoneCapture:
    def __init__(self, audio_callback=None):
        """Initialize phone audio capture using sockets.
        
        Args:
            audio_callback: Function to call with audio data when received
        """
        self.host = SOCKET_HOST
        self.port = SOCKET_PORT
        self.socket = None
        self.running = False
        self.audio_callback = audio_callback
        self.thread = None
    
    def start(self):
        """Start listening for incoming phone audio data."""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.host, self.port))
        self.socket.listen(5)
        
        self.running = True
        self.thread = threading.Thread(target=self._listen_for_connections)
        self.thread.daemon = True
        self.thread.start()
        
        print(f"Phone capture server listening on {self.host}:{self.port}")
        print("To use with Twilio:")
        print(f"1. Set up ngrok: 'ngrok tcp {self.port}'")
        print("2. Configure your Twilio webhook to send audio to this server")
    
    def stop(self):
        """Stop listening for phone audio."""
        self.running = False
        if self.socket:
            self.socket.close()
        if self.thread:
            self.thread.join(timeout=1)
    
    def _listen_for_connections(self):
        """Listen for incoming connections."""
        while self.running:
            try:
                client_socket, client_address = self.socket.accept()
                print(f"Connection from {client_address}")
                client_thread = threading.Thread(
                    target=self._handle_client,
                    args=(client_socket,)
                )
                client_thread.daemon = True
                client_thread.start()
            except Exception as e:
                if self.running:
                    print(f"Error accepting connection: {e}")
    
    def _handle_client(self, client_socket):
        """Handle incoming client connection and data."""
        buffer = b""
        
        while self.running:
            try:
                data = client_socket.recv(4096)
                if not data:
                    break
                
                buffer += data
                
                # Try to parse complete JSON messages
                while b'\n' in buffer:
                    message, buffer = buffer.split(b'\n', 1)
                    try:
                        parsed = json.loads(message)
                        self._process_message(parsed)
                    except json.JSONDecodeError:
                        print("Failed to parse message as JSON")
            
            except Exception as e:
                print(f"Error handling client: {e}")
                break
        
        client_socket.close()
    
    def _process_message(self, message):
        """Process a message received from the phone call."""
        if message.get('event') == 'media':
            payload = message.get('media', {}).get('payload')
            if payload:
                # Decode base64 audio data
                audio_data = base64.b64decode(payload)
                # Convert to numpy array
                audio_array = np.frombuffer(audio_data, dtype=np.int16)
                
                # Call the callback if available
                if self.audio_callback:
                    self.audio_callback(audio_array)


def simple_test():
    """Simple test for the phone capture module."""
    def audio_received(audio_data):
        print(f"Received audio chunk: {len(audio_data)} samples, max amplitude: {np.max(np.abs(audio_data))}")
    
    phone = PhoneCapture(audio_callback=audio_received)
    try:
        phone.start()
        # Keep the server running for testing
        input("Press Enter to stop the server...\n")
    finally:
        phone.stop()

if __name__ == "__main__":
    simple_test()