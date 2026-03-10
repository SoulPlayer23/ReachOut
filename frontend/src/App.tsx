import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Landing from './pages/Landing'
import Login from './pages/Login'
import Register from './pages/Register'
import OnboardingResume from './pages/onboarding/Resume'
import OnboardingPreferences from './pages/onboarding/Preferences'
import OnboardingConnections from './pages/onboarding/Connections'
import Chat from './pages/app/Chat'
import Sources from './pages/app/Sources'
import History from './pages/app/History'
import Settings from './pages/app/Settings'

function PrivateRoute({ children }: { children: React.ReactNode }) {
  const token = localStorage.getItem('token')
  return token ? <>{children}</> : <Navigate to="/login" replace />
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />

        <Route path="/onboarding/resume" element={<PrivateRoute><OnboardingResume /></PrivateRoute>} />
        <Route path="/onboarding/preferences" element={<PrivateRoute><OnboardingPreferences /></PrivateRoute>} />
        <Route path="/onboarding/connections" element={<PrivateRoute><OnboardingConnections /></PrivateRoute>} />

        <Route path="/app/chat" element={<PrivateRoute><Chat /></PrivateRoute>} />
        <Route path="/app/sources" element={<PrivateRoute><Sources /></PrivateRoute>} />
        <Route path="/app/history" element={<PrivateRoute><History /></PrivateRoute>} />
        <Route path="/app/settings" element={<PrivateRoute><Settings /></PrivateRoute>} />
      </Routes>
    </BrowserRouter>
  )
}
