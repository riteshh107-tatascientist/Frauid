// frontend/src/pages/DashboardPage.tsx
import { useContext, useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { AuthContext } from '../App'

export default function DashboardPage() {
  const auth = useContext(AuthContext)
  const navigate = useNavigate()
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchUserData = async () => {
      if (!auth?.token) {
        navigate('/login')
        return
      }

      try {
        const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/auth/me`, {
          headers: {
            Authorization: `Bearer ${auth.token}`,
          },
        })

        if (!response.ok) {
          auth.logout()
          navigate('/login')
        }
      } catch (error) {
        console.error('Error fetching user:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchUserData()
  }, [auth, navigate])

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-dark flex items-center justify-center">
        <div className="text-white">Loading...</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-dark p-8">
      <div className="max-w-6xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-4xl font-bold text-white">FraudGuard AI Dashboard</h1>
          <button
            onClick={() => {
              auth?.logout()
              navigate('/login')
            }}
            className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded"
          >
            Logout
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <div className="bg-dark-secondary p-6 rounded-lg">
            <h3 className="text-gray-400 text-sm font-medium">Total Transactions</h3>
            <p className="text-3xl font-bold text-white mt-2">--</p>
          </div>
          <div className="bg-dark-secondary p-6 rounded-lg">
            <h3 className="text-gray-400 text-sm font-medium">Fraud Detected</h3>
            <p className="text-3xl font-bold text-accent-red mt-2">--</p>
          </div>
          <div className="bg-dark-secondary p-6 rounded-lg">
            <h3 className="text-gray-400 text-sm font-medium">High Risk</h3>
            <p className="text-3xl font-bold text-accent-yellow mt-2">--</p>
          </div>
          <div className="bg-dark-secondary p-6 rounded-lg">
            <h3 className="text-gray-400 text-sm font-medium">Avg Risk Score</h3>
            <p className="text-3xl font-bold text-accent-blue mt-2">--</p>
          </div>
        </div>

        <div className="bg-dark-secondary p-6 rounded-lg">
          <h2 className="text-xl font-bold text-white mb-4">Dashboard coming in Phase 5...</h2>
          <p className="text-gray-400">
            Phase 1: ✅ Backend foundation<br />
            Phase 2: ⏳ ML pipeline<br />
            Phase 3: ⏳ Prediction API<br />
            Phase 4: ⏳ Authentication<br />
            Phase 5: ⏳ Dashboard & UI
          </p>
        </div>
      </div>
    </div>
  )
}
