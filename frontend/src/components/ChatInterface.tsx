import { useState, useRef, useEffect } from 'react'
import { processInput } from '../services/api'
import MicInput from './MicInput'
import EmotionDisplay from './EmotionDisplay'
import { Loader, Send } from 'lucide-react'

interface Message {
  id: string
  type: 'user' | 'ai'
  text: string
  emotion?: {
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
  metrics?: {
    latency_ms: number
    tokens_out: number
    total_latency_ms: number
    grounding: number
    hallucination: number
  }
}

export default function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([])
  const [inputValue, setInputValue] = useState('')
  const [loading, setLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const [selectedEmotion, setSelectedEmotion] = useState<Message | null>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleMicInput = async (transcript: string) => {
    await handleSubmit(transcript)
  }

  const handleSubmit = async (text?: string) => {
    const inputText = text || inputValue.trim()
    if (!inputText) return

    setLoading(true)
    const userMessageId = Date.now().toString()
    
    const userMessage: Message = {
      id: userMessageId,
      type: 'user',
      text: inputText,
    }
    
    setMessages((prev) => [...prev, userMessage])
    setInputValue('')

    try {
      const response = await processInput(inputText)
      
      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'ai',
        text: response.response,
        emotion: response.emotion,
        metrics: response.metrics,
      }
      
      setMessages((prev) => [...prev, aiMessage])
    } catch (error) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'ai',
        text: 'Sorry, there was an error processing your input. Make sure the backend is running.',
      }
      setMessages((prev) => [...prev, errorMessage])
    } finally {
      setLoading(false)
    }
  }

  const emotionEmoji = {
    fear: '😨',
    surprise: '😲',
    anger: '😠',
    joy: '😊',
    sadness: '😔',
    neutral: '😐',
    disgust: '🤢',
  } as Record<string, string>

  return (
    <div className="flex h-screen w-full">
      {/* Chat Container */}
      <div className="flex-1 flex flex-col max-w-4xl mx-auto w-full">
        {/* Header */}
        <div className="bg-white shadow-sm border-b border-gray-200 px-6 py-4">
          <h1 className="text-3xl font-bold text-gray-800">Voice Emotion RAG</h1>
          <p className="text-sm text-gray-600 mt-1">
            Speak or type to get personalized emotional support
          </p>
        </div>

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {messages.length === 0 ? (
            <div className="flex items-center justify-center h-full">
              <div className="text-center">
                <div className="text-6xl mb-4">🎤</div>
                <h2 className="text-2xl font-bold text-gray-800 mb-2">
                  Welcome to Voice Emotion RAG
                </h2>
                <p className="text-gray-600">
                  Click the microphone below or type to share how you're feeling
                </p>
              </div>
            </div>
          ) : (
            <>
              {messages.map((message) => (
                <div key={message.id} className="space-y-3">
                  <div
                    className={`flex ${
                      message.type === 'user' ? 'justify-end' : 'justify-start'
                    }`}
                  >
                    <div
                      className={`max-w-2xl px-4 py-3 rounded-lg ${
                        message.type === 'user'
                          ? 'bg-indigo-600 text-white rounded-br-none'
                          : 'bg-white text-gray-800 shadow-sm rounded-bl-none border border-gray-200'
                      }`}
                    >
                      <p className="text-sm">{message.text}</p>
                    </div>
                  </div>

                  {/* Emotion Display */}
                  {message.emotion && (
                    <div
                      className="flex justify-start cursor-pointer hover:opacity-80 transition"
                      onClick={() =>
                        setSelectedEmotion(
                          selectedEmotion?.id === message.id ? null : message
                        )
                      }
                    >
                      <div className="max-w-2xl">
                        <EmotionDisplay emotion={message.emotion} />
                      </div>
                    </div>
                  )}

                  {/* Metrics */}
                  {message.metrics && (
                    <div className="flex justify-start">
                      <div className="max-w-2xl bg-gradient-to-r from-purple-50 to-blue-50 border border-purple-100 rounded-lg p-3 text-sm text-gray-700">
                        <div className="grid grid-cols-2 gap-3">
                          <div>
                            <span className="font-semibold">Response time:</span>{' '}
                            {message.metrics.latency_ms}ms
                          </div>
                          <div>
                            <span className="font-semibold">Tokens:</span>{' '}
                            {message.metrics.tokens_out}
                          </div>
                          <div>
                            <span className="font-semibold">Grounding:</span>{' '}
                            {(message.metrics.grounding * 100).toFixed(1)}%
                          </div>
                          <div>
                            <span className="font-semibold">Hallucination:</span>{' '}
                            {(message.metrics.hallucination * 100).toFixed(1)}%
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              ))}
              <div ref={messagesEndRef} />
            </>
          )}
        </div>

        {/* Input Area */}
        <div className="bg-white border-t border-gray-200 p-6 space-y-4">
          {/* Mic Input */}
          <div className="flex justify-center">
            <MicInput
              onTranscript={handleMicInput}
              disabled={loading}
            />
          </div>

          {/* Text Input */}
          <div className="flex gap-2">
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={(e) => {
                if (e.key === 'Enter' && !loading) {
                  handleSubmit()
                }
              }}
              placeholder="Or type how you're feeling..."
              disabled={loading}
              className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-600 disabled:bg-gray-100"
            />
            <button
              onClick={() => handleSubmit()}
              disabled={loading || !inputValue.trim()}
              className="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:bg-gray-400 flex items-center gap-2 transition"
            >
              {loading ? (
                <Loader className="w-5 h-5 animate-spin" />
              ) : (
                <Send className="w-5 h-5" />
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Emotion Sidebar */}
      {selectedEmotion && selectedEmotion.emotion && (
        <div className="w-64 bg-white border-l border-gray-200 p-6 overflow-y-auto">
          <h3 className="font-bold text-lg mb-4">Emotion Breakdown</h3>
          <EmotionDisplay emotion={selectedEmotion.emotion} expanded />
        </div>
      )}
    </div>
  )
}
