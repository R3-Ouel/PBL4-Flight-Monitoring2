import { Navigate, createBrowserRouter } from 'react-router-dom'
import { DashboardLayout } from './components/layout/DashboardLayout'
import { AnalysePage } from './pages/AnalysePage'
import { NavigationPage } from './pages/NavigationPage'
import { CameraPage } from './pages/CameraPage'

export const router = createBrowserRouter([
  {
    path: '/',
    element: <DashboardLayout />,
    children: [
      { index: true, element: <Navigate to="/analyse" replace /> },
      { path: 'analyse', element: <AnalysePage /> },
      { path: 'navigation', element: <NavigationPage /> },
      { path: 'camera', element: <CameraPage /> },
    ],
  },
  { path: '*', element: <Navigate to="/analyse" replace /> },
])
