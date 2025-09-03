import { useEffect, useState } from 'react'
import UserResponse from "./components/UserReponse"

import './App.css'

type Hello = { message: string }

function App() {
  const [msg, setMsg] = useState<string>('Loading...')
  const [status, setStatus] = useState<string>('checking...')

  useEffect(() => {
    // Health check (optional)
    fetch('/health')
      .then(r => r.json())
      .then(data => setStatus(data.status ?? 'unknown'))
      .catch(() => setStatus('unreachable'))

    // Call your Flask API
    fetch('/api/hello')
      .then(r => r.json())
      .then((data: Hello) => setMsg(data.message))
      .catch(err => setMsg(`Request failed: ${err}`))
  }, [])

  return (
    <main style={{ fontFamily: 'system-ui, Arial', margin: '3rem auto', maxWidth: 720 }}>
      <h1>React ⟷ Flask</h1>
      <p><strong>Backend health:</strong> {status}</p>
      <p><strong>API says:</strong> {msg}</p>
      <div className="App">
        <p>
          <a href="/login">Sign in</a>
        </p>
        <p>
          <a href="/logout">Sign out</a>
        </p>
      </div>
      <UserResponse />
    </main>
  )
}

export default App
