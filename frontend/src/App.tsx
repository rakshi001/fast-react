import { useEffect } from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import { useAuthStore } from "./store/useAuthStore";
import Layout from "./components/layout/Layout";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";

/**
 * ============================================================================
 * ROOT APPLICATION & ROUTING (React Router)
 * ============================================================================
 * The `App` component is the absolute root of our visual React application.
 * 
 * Primary Responsibilities:
 * 1. App Initialization: It attempts to fetch the current user using the saved JWT
 *    token *before* deciding what page to show.
 * 2. Routing: It uses React Router to map URLs (like `/login` or `/`) to 
 *    specific Component files.
 * 3. Route Protection: It prevents unauthenticated users from seeing the Dashboard,
 *    and prevents authenticated users from going back to the Login page.
 * ============================================================================
 */

function App() {
  // Grab our authentication state from the Global Zustand store
  const { fetchCurrentUser, isLoading, isAuthenticated } = useAuthStore();

  // useEffect runs ONCE when the app first loads in the browser.
  // It triggers the API call to /auth/me to verify our token.
  useEffect(() => {
    fetchCurrentUser();
  }, [fetchCurrentUser]);

  // While the API is checking our token, show a spinning loading circle.
  // Without this, the app might temporarily flash the Login page even if we are logged in.
  if (isLoading) {
    return (
      <div className="flex h-screen w-screen items-center justify-center bg-muted/40">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <Router>
      <Routes>
        {/* 
          UNPROTECTED ROUTES 
          If the user is already authenticated, force them to the Dashboard instead.
        */}
        <Route
          path="/login"
          element={isAuthenticated ? <Navigate to="/" replace /> : <Login />}
        />
        <Route
          path="/register"
          element={isAuthenticated ? <Navigate to="/" replace /> : <Register />}
        />
        
        {/* 
          PROTECTED ROUTES (The Layout)
          <Layout /> wraps all routes nested inside it. Inside Layout.tsx, we check 
          if the user is authenticated. If they aren't, Layout.tsx kicks them to `/login`.
        */}
        <Route path="/" element={<Layout />}>
          {/* Think of `index` as the default page to show inside the Layout for the `/` path */}
          <Route index element={<Dashboard />} />
        </Route>
        
        {/* 
          CATCH-ALL ("Wildcard") ROUTE
          If the user types a URL that doesn't exist (like `/garbage`), redirect them back to `/`.
        */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  );
}

export default App;
