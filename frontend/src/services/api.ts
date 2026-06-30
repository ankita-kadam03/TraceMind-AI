import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
})

export interface ProcessResponse {
  response: string
  emotion: {
    fear: number
    surprise: number
    anger: number
    joy: number
    sadness: number
    neutral: number
    disgust: number
    top_emotion: string
    top_score: number
  }
  metrics: {
    latency_ms: number
    tokens_out: number
    total_latency_ms: number
    grounding: number
    hallucination: number
  }
}

export async function processInput(text: string): Promise<ProcessResponse> {
  try {
    const response = await api.post<ProcessResponse>('/process', { text })
    return response.data
  } catch (error) {
    console.error('API Error:', error)
    throw error
  }
}

export async function transcribeAudio(audioBlob: Blob): Promise<{ transcript: string }> {
  try {
    const formData = new FormData()
    formData.append('audio', audioBlob)
    
    const response = await api.post<{ transcript: string }>('/transcribe', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    
    return response.data
  } catch (error) {
    console.error('Transcription Error:', error)
    throw error
  }
}

export default api
