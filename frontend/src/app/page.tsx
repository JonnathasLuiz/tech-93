'use client';

import { useState, useRef, useEffect } from 'react';

export default function Home() {
  const [isRecording, setIsRecording] = useState(false);
  const [status, setStatus] = useState('Idle');
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);

  useEffect(() => {
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  const startRecording = async () => {
    setStatus('Requesting permissions...');
    try {
      const micStream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const displayStream = await navigator.mediaDevices.getDisplayMedia({ video: true, audio: true });

      const audioContext = new AudioContext();
      audioContextRef.current = audioContext;

      const micSource = audioContext.createMediaStreamSource(micStream);

      const displayAudioTrack = displayStream.getAudioTracks()[0];
      if (!displayAudioTrack) {
        alert("Your selected display source does not provide audio. Please select a Tab or Window that does.");
        setStatus('Error: No display audio');
        micStream.getTracks().forEach(track => track.stop());
        displayStream.getTracks().forEach(track => track.stop());
        return;
      }
      const displaySource = audioContext.createMediaStreamSource(new MediaStream([displayAudioTrack]));

      const mixedStream = audioContext.createMediaStreamDestination();
      micSource.connect(mixedStream);
      displaySource.connect(mixedStream);

      setStatus('Connecting to server...');
      const ws = new WebSocket('ws://localhost:8000/ws');
      wsRef.current = ws;

      ws.onopen = () => {
        setStatus('Connected. Starting recording...');
        const recorder = new MediaRecorder(mixedStream.stream, { mimeType: 'audio/webm;codecs=opus' });
        mediaRecorderRef.current = recorder;

        recorder.ondataavailable = (event) => {
          if (event.data.size > 0 && ws.readyState === WebSocket.OPEN) {
            ws.send(event.data);
          }
        };

        recorder.onstart = () => {
          setIsRecording(true);
          setStatus('Recording...');
        };

        recorder.onstop = () => {
            setIsRecording(false);
            setStatus('Recording stopped.');
            micStream.getTracks().forEach(track => track.stop());
            displayStream.getTracks().forEach(track => track.stop());
            if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
                wsRef.current.close();
            }
        };

        recorder.start(1000);
      };

      ws.onerror = (error) => {
        console.error('WebSocket Error:', error);
        setStatus('WebSocket Error. Check console.');
        stopRecording();
      };

      ws.onclose = () => {
        setStatus('Disconnected from server.');
        if (isRecording) {
            stopRecording();
        }
      };

    } catch (error) {
      console.error('Error starting recording:', error);
      setStatus(`Error: ${(error as Error).message}`);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
      mediaRecorderRef.current.stop();
    }
     if (audioContextRef.current && audioContextRef.current.state !== 'closed') {
      audioContextRef.current.close();
    }
  };

  const handleToggleRecording = () => {
    if (isRecording) {
      stopRecording();
    } else {
      startRecording();
    }
  };

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24 bg-gray-900 text-white">
      <div className="z-10 w-full max-w-5xl items-center justify-between font-mono text-sm lg:flex flex-col text-center">
        <h1 className="text-4xl font-bold mb-8">The Architect - Real-time Meeting Intelligence</h1>
        <p className="mb-4 text-lg">
          Press "Start Recording" to begin capturing your microphone and system audio.
        </p>
        <p className="mb-8 text-md text-yellow-400">
            Important: You must use headphones to prevent echo.
        </p>
        <div className="flex items-center justify-center space-x-4 mt-4">
            <button
            onClick={handleToggleRecording}
            className={`px-8 py-4 text-xl font-bold rounded-lg transition-colors
                ${isRecording
                ? 'bg-red-600 hover:bg-red-700'
                : 'bg-blue-600 hover:bg-blue-700'
                }`}
            >
            {isRecording ? 'Stop Recording' : 'Start Recording'}
            </button>
            <div className="text-lg p-4 bg-gray-800 rounded-lg">
                <strong>Status:</strong> <span className="font-light">{status}</span>
            </div>
        </div>
      </div>
    </main>
  );
}
