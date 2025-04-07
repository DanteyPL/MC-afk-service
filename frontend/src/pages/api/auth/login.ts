import type { NextApiRequest, NextApiResponse } from 'next'

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== 'POST') {
    return res.status(405).json({ message: 'Method not allowed' })
  }

  try {
    let body = req.body
    if (typeof body === 'string') {
      try {
        body = JSON.parse(body)
      } catch (e) {
        return res.status(400).json({ message: 'Invalid JSON format' })
      }
    }

    // Accept both 'username' and 'email' fields from frontend
    const email = body.email || body.username
    const { password } = body

    if (!email?.trim()) {
      return res.status(400).json({ 
        message: 'Email/username is required',
        receivedFields: Object.keys(body)
      })
    }

    if (!password) {
      return res.status(400).json({ 
        message: 'Password is required',
        receivedFields: Object.keys(body)
      })
    }

    if (!process.env.NEXT_PUBLIC_API_URL) {
      throw new Error('API_URL is not configured')
    }

    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/login`, {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify({
        email: email.trim(),
        password
      })
    })

    const responseData = await response.json()

    if (!response.ok) {
      return res.status(response.status).json(responseData)
    }

    return res.status(200).json(responseData)
  } catch (err) {
    console.error('Login error:', err)
    return res.status(500).json({ 
      message: 'Internal server error',
      error: err instanceof Error ? err.message : 'Unknown error'
    })
  }
}