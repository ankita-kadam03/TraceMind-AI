import { FC } from 'react'

interface Emotion {
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

interface EmotionDisplayProps {
  emotion: Emotion
  expanded?: boolean
}

const EmotionDisplay: FC<EmotionDisplayProps> = ({ emotion, expanded = false }) => {
  const emotionEmoji = {
    fear: '😨',
    surprise: '😲',
    anger: '😠',
    joy: '😊',
    sadness: '😔',
    neutral: '😐',
    disgust: '🤢',
  } as Record<string, string>

  const emotionColors = {
    fear: 'from-orange-100 to-orange-50',
    surprise: 'from-yellow-100 to-yellow-50',
    anger: 'from-red-100 to-red-50',
    joy: 'from-green-100 to-green-50',
    sadness: 'from-blue-100 to-blue-50',
    neutral: 'from-gray-100 to-gray-50',
    disgust: 'from-purple-100 to-purple-50',
  } as Record<string, string>

  const sortedEmotions = Object.entries(emotion)
    .filter(([key]) => key !== 'top_emotion' && key !== 'top_score')
    .sort(([, a], [, b]) => (b as number) - (a as number))

  if (!expanded) {
    return (
      <div className={`bg-gradient-to-r ${emotionColors[emotion.top_emotion]} border border-orange-200 rounded-lg p-4`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-3xl">
              {emotionEmoji[emotion.top_emotion]}
            </span>
            <div>
              <p className="font-semibold text-gray-800 capitalize">
                {emotion.top_emotion}
              </p>
              <p className="text-sm text-gray-600">
                {(emotion.top_score * 100).toFixed(1)}% confidence
              </p>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-3">
      <div className={`bg-gradient-to-r ${emotionColors[emotion.top_emotion]} border border-gray-200 rounded-lg p-4`}>
        <div className="flex items-center gap-3 mb-3">
          <span className="text-4xl">
            {emotionEmoji[emotion.top_emotion]}
          </span>
          <div>
            <p className="font-bold text-gray-800 capitalize text-lg">
              {emotion.top_emotion}
            </p>
            <p className="text-sm text-gray-700">
              {(emotion.top_score * 100).toFixed(1)}% confidence
            </p>
          </div>
        </div>
      </div>

      <div className="space-y-2">
        {sortedEmotions.map(([emotionName, score]) => (
          <div key={emotionName}>
            <div className="flex items-center justify-between mb-1">
              <span className="text-sm font-medium text-gray-700 flex items-center gap-2">
                <span>{emotionEmoji[emotionName]}</span>
                <span className="capitalize">{emotionName}</span>
              </span>
              <span className="text-xs font-semibold text-gray-600">
                {((score as number) * 100).toFixed(1)}%
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-indigo-600 h-2 rounded-full transition-all"
                style={{ width: `${((score as number) * 100)}%` }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default EmotionDisplay
