import { useState, useRef } from 'react'
import { Mic, Square } from 'lucide-react'

interface MicInputProps {
  onTranscript: (transcript: string) => void
  disabled?: boolean
}

export default function MicInput({ onTranscript, disabled = false }: MicInputProps) {
  const [isRecording, setIsRecording] = useState(false)
  const [isProcessing, setIsProcessing] = useState(false)
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const chunksRef = useRef<Blob[]>([])

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const mediaRecorder = new MediaRecorder(stream)
      mediaRecorderRef.current = mediaRecorder
      chunksRef.current = []

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          chunksRef.current.push(e.data)
        }
      }

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(chunksRef.current, { type: 'audio/wav' })
        stream.getTracks().forEach((track) => track.stop())
        
        setIsProcessing(true)
        try {
          // Send to backend for transcription
          const formData = new FormData()
          formData.append('audio', audioBlob, 'recording.wav')
          
          const response = await fetch('/api/transcribe', {
            method: 'POST',
            body: formData,
          })
          
          if (response.ok) {
            const data = await response.json()
            onTranscript(data.transcript)
          } else {
            console.error('Transcription failed')
          }
        } finally {
          setIsProcessing(false)
        }
      }

      mediaRecorder.start()
      setIsRecording(true)
    } catch (error) {
      console.error('Error accessing microphone:', error)
      alert('Please allow microphone access to use this feature')
    }
  }

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop()
      setIsRecording(false)
    }
  }

  return (
    <button
      onClick={isRecording ? stopRecording : startRecording}
      disabled={disabled || isProcessing}
      className={`flex items-center justify-center w-20 h-20 rounded-full transition-all ${
        isRecording
          ? 'bg-red-500 hover:bg-red-600 scale-110 mic-button-pulse'
          : 'bg-indigo-600 hover:bg-indigo-700'
      } text-white disabled:bg-gray-400 shadow-lg`}
      title={isRecording ? 'Stop recording' : 'Start recording'}
    >
      {isProcessing ? (
        <span className="animate-spin">⏳</span>
      ) : isRecording ? (
        <Square className="w-8 h-8" />
      ) : (
        <Mic className="w-8 h-8" />
      )}
    </button>
  )
}
