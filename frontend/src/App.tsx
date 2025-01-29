import { useState } from 'react'
import { ThreeDots } from 'react-loading-icons'
import axios from 'axios'

type Tweet = {
  content: string
  virality_score: number
  justification: string
}

function App() {
  const [topic, setTopic] = useState('')
  const [tweets, setTweets] = useState<Tweet[]>([])
  const [selectedTweets, setSelectedTweets] = useState<string[]>([])
  const [loading, setLoading] = useState(false)

  const generateTweets = async () => {
    setLoading(true)
    try {
      const response = await axios.post('http://localhost:8000/generate-tweets', {
        topic
      })
      setTweets(response.data.tweets)
    } catch (error) {
      alert('Error generating tweets')
    }
    setLoading(false)
  }

  const postTweets = async () => {
    try {
      await axios.post('http://localhost:8000/post-tweets', {
        tweets: selectedTweets
      })
      alert('Tweets posted successfully!')
      setSelectedTweets([])
    } catch (error) {
      alert('Error posting tweets')
    }
  }

  return (
    <div className="min-h-screen bg-dark-primary text-gray-100 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold mb-8 text-accent">Xpresso</h1>
        
        {/* Topic Input */}
        <div className="flex gap-4 mb-12">
          <input
            type="text"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            placeholder="Enter your topic..."
            className="flex-1 p-4 rounded-lg bg-dark-secondary border border-gray-700 focus:outline-none focus:border-accent"
          />
          <button
            onClick={generateTweets}
            disabled={loading}
            className="px-6 py-3 bg-accent hover:bg-indigo-700 rounded-lg font-semibold transition-colors disabled:opacity-50"
          >
            {loading ? <ThreeDots height="1.5em" fill="#FFF" /> : 'Generate Tweets'}
          </button>
        </div>

        {/* Tweets Grid */}
        {tweets.length > 0 && (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-semibold">Generated Tweets</h2>
              <button
                onClick={postTweets}
                disabled={selectedTweets.length === 0}
                className="px-4 py-2 bg-green-600 hover:bg-green-700 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Post Selected ({selectedTweets.length})
              </button>
            </div>
            
            <div className="grid gap-4">
              {tweets.map((tweet, index) => (
                <div 
                  key={index}
                  className={`p-4 rounded-lg bg-dark-secondary border-2 transition-all 
                    ${selectedTweets.includes(tweet.content) ? 'border-accent' : 'border-dark-secondary'}`}
                >
                  <label className="flex gap-4 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={selectedTweets.includes(tweet.content)}
                      onChange={(e) => {
                        if (e.target.checked) {
                          setSelectedTweets([...selectedTweets, tweet.content])
                        } else {
                          setSelectedTweets(selectedTweets.filter(t => t !== tweet.content))
                        }
                      }}
                      className="mt-1 accent-accent"
                    />
                    <div>
                      <p className="mb-2">{tweet.content}</p>
                      <div className="flex gap-2 text-sm text-gray-400">
                        <span>Score: {tweet.virality_score}</span>
                        <span>•</span>
                        <span>{tweet.justification}</span>
                      </div>
                    </div>
                  </label>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default App