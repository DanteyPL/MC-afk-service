import type { NextApiRequest, NextApiResponse } from 'next'
import axios from 'axios'

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== 'POST') {
    return res.status(405).json({ message: 'Method not allowed' })
  }

  try {
    if (!process.env.NEXT_PUBLIC_API_URL) {
      throw new Error('API_URL is not configured')
    }

    const response = await axios.post(`${process.env.NEXT_PUBLIC_API_URL}/minecraft/start`, req.body)
    return res.status(200).json(response.data)
  } catch (err) {
    console.error('Start Minecraft error:', err)
    return res.status(500).json({ 
      message: 'Failed to start Minecraft server',
      error: err instanceof Error ? err.message : 'Unknown error'
    })
  }
}
