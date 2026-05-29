import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { RouterProvider } from 'react-router-dom'
import './index.css'
import './store/useAppStore'
import { router } from './router'
import './services/flightService'
import { FlightProvider } from './contexts/FlightContext'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <FlightProvider>
      <RouterProvider router={router} />
    </FlightProvider>
  </StrictMode>,
)
