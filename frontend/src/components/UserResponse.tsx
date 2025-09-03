import { useState } from 'react'

type MeResponse =
  | { authenticated: false }
  | {
    authenticated: true
    user: {
      id: string | null
      email: string | null
      first_name?: string | null
      last_name?: string | null
      email_verified?: boolean | null
      profile_photo_url?: string | null
    }
  }

export default function UserResponse() {
  const [me, setMe] = useState<MeResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  console.log('authenticated', me)

  async function fetchMe() {
    try {
      setLoading(true)
      setError(null)
      const res = await fetch('/api/me', {
        credentials: 'include', // send wos_session cookie
      })
      if (res.status === 401) {
        setMe({ authenticated: false })
      } else {
        const data = (await res.json()) as MeResponse
        console.log('Fetched /dashboard:', data)
        setMe(data)
      }
    } catch (e: any) {
      setError(e?.message ?? 'Failed to fetch user')
    } finally {
      setLoading(false)
    }
  }

  const name =
    me && 'user' in me
      ? [me.user.first_name, me.user.last_name].filter(Boolean).join(' ')
      : ''

  return (
    <main style={{ fontFamily: 'system-ui, Arial', margin: '3rem auto', maxWidth: 720 }}>
      <h1>Welcome</h1>

      {loading && <p>Refresh to see User Info</p>}
      {error && <p style={{ color: 'crimson' }}>{error}</p>}

      {!loading && me?.authenticated === true && 'user' in me && (
        <section style={{ textAlign: 'center', marginTop: '2rem' }}>
          {me.user.profile_photo_url && (
            <img
              src={me.user.profile_photo_url}
              alt="Profile"
              width={64}
              height={64}
              style={{ borderRadius: '50%', marginBottom: '1rem' }}
            />
          )}

          <div style={{ fontSize: 18, fontWeight: 600 }}>
            {name || me.user.email}
          </div>
          <div style={{ color: '#aaa' }}>{me.user.email}</div>
          {me.user.email_verified !== undefined && (
            <div style={{ color: me.user.email_verified ? 'green' : 'orange' }}>
              {me.user.email_verified ? 'Email verified' : 'Email not verified'}
            </div>
          )}
        </section>
      )}

      {
        !loading && me?.authenticated === false && (
          <section style={{ textAlign: 'center', marginTop: '2rem' }}>
            <p>You are not logged in</p>
          </section>
        )
      }


      <hr style={{ margin: '2rem 0' }} />
      <button onClick={fetchMe}>Refresh</button>
    </main>
  )
}
