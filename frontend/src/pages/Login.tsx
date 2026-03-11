import { useState } from "react";
import { useAuthStore } from "@/store/useAuthStore";
import { authApi } from "@/api/services";
import { useNavigate, Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";

/**
 * ============================================================================
 * REACT COMPONENT - Login Page
 * ============================================================================
 * This is a visual UI component. It handles the local state of the input fields,
 * makes the API call to log in, and then uses the Global Zustand store to 
 * save the resulting token.
 * ============================================================================
 */
export default function Login() {
  // --- LOCAL STATE ---
  // useState hooks manage data that only this specific screen cares about.
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  
  // --- GLOBAL STATE ---
  // We grab the `login` function from our Zustand store.
  const login = useAuthStore((state) => state.login);
  
  // React Router hook to programmatically navigate to different pages
  const navigate = useNavigate();

  // --- FORM SUBMISSION ---
  const handleSubmit = async (e: React.FormEvent) => {
    // 1. Prevent the browser from refreshing the page (default HTML form behavior)
    e.preventDefault();
    setError(""); // Clear any previous errors
    
    try {
      // 2. Call our backend API via the Axios wrapper
      const data = await authApi.login({ email, password });
      
      // 3. If successful, pass the token to Zustand. 
      //    Zustand will save it to LocalStorage and update the Global React state.
      login(data.access_token);
      
      // 4. Redirect the user to the Dashboard ("/")
      navigate("/");
    } catch (err: any) {
      // 5. If the backend throws a 401 Unauthorized, display the error message on screen
      setError(err.response?.data?.detail || "Login failed");
    }
  };

  return (
    <div className="flex h-screen w-full items-center justify-center bg-muted/40">
      {/* Shadcn UI Card components give us beautifully pre-styled boxes */}
      <Card className="w-full max-w-sm">
        <CardHeader>
          <CardTitle className="text-2xl">Login</CardTitle>
          <CardDescription>Enter your email below to login to your account.</CardDescription>
        </CardHeader>
        
        {/* Form bound to our handleSubmit function */}
        <form onSubmit={handleSubmit}>
          <CardContent className="grid gap-4">
            
            {/* Conditional Rendering: Only show error div if the error string is not empty */}
            {error && <div className="text-sm text-destructive font-medium">{error}</div>}
            
            <div className="grid gap-2">
              <Label htmlFor="email">Email</Label>
              {/* Controlled Input: The UI updates the `email` state, and the state dictates what the UI shows */}
              <Input
                id="email"
                type="email"
                placeholder="m@example.com"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>
            
            <div className="grid gap-2">
              <Label htmlFor="password">Password</Label>
              <Input
                id="password"
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>
            
          </CardContent>
          <CardFooter className="flex-col gap-4">
            <Button type="submit" className="w-full">
              Sign in
            </Button>
            <div className="text-center text-sm">
              Don&apos;t have an account?{" "}
              {/* Link component avoids full page reload, acting like an internal app transition */}
              <Link to="/register" className="underline underline-offset-4">
                Sign up
              </Link>
            </div>
          </CardFooter>
        </form>
      </Card>
    </div>
  );
}
