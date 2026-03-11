import { create } from "zustand";
import { apiClient } from "@/api/client";

export interface User {
  id: number;
  email: string;
  full_name: string;
  is_active: boolean;
  created_at: string;
}

/**
 * ============================================================================
 * STATE MANAGEMENT (Zustand) - Authentication Store
 * ============================================================================
 * What is Zustand?
 * It's a "Global State Manager" for React. 
 * 
 * The Problem: 
 * If User logs in on the "LoginPage", how does the "Navbar" know their name?
 * You *could* pass the user object down through 10 layers of components (App -> Layout -> Header -> Navbar)
 * but that's called "Prop Drilling" and it gets extremely messy.
 * 
 * The Solution:
 * Zustand creates a "Global Store". Any component in the app can instantly grab
 * data out of this store, or update data inside of it, without passing props.
 * ============================================================================
 */

// 1. Defining the "Shape" of our Store
interface AuthState {
  user: User | null;         // The currently logged-in user profile
  token: string | null;      // The JWT String
  isAuthenticated: boolean;  // Quick boolean check
  isLoading: boolean;        // Is the app still checking the token on initial load?
  
  // Functions to modify the state
  login: (token: string) => void;
  logout: () => void;
  fetchCurrentUser: () => Promise<void>;
}

// 2. Creating the Store
export const useAuthStore = create<AuthState>((set, get) => ({
  // --- INITIAL VALUES ---
  user: null,
  // We initialize by checking if a token is sitting in the browser's Local Storage from a previous session
  token: localStorage.getItem("kw_token"),
  isAuthenticated: !!localStorage.getItem("kw_token"), 
  isLoading: true, // We start as 'loading' until we verify if the local token is actually valid

  // --- ACTIONS ---
  
  // When the user submits the Login Form, this function runs.
  login: (token: string) => {
    localStorage.setItem("kw_token", token); // Save to browser storage so it persists across refreshes
    set({ token, isAuthenticated: true });   // Update the Global React State
    get().fetchCurrentUser();                // Immediately go fetch the user's name/email using the new token
  },

  // When the user clicks Logout
  logout: () => {
    localStorage.removeItem("kw_token");     // Delete the token
    // Wipe the Global React State clean
    set({ user: null, token: null, isAuthenticated: false, isLoading: false }); 
  },

  // This runs when the App first loads to check if the session is still valid
  fetchCurrentUser: async () => {
    const { token, logout } = get();
    
    // If there's no token in storage, just stop loading and show the login page
    if (!token) {
      set({ isLoading: false });
      return;
    }

    try {
      // Send a request to the backend. (Our Axios interceptor will automatically attach the token!)
      const response = await apiClient.get<User>("/auth/me");
      
      // If successful, the token is valid! Update the state with the user's real data.
      set({ user: response.data, isAuthenticated: true, isLoading: false });
    } catch (error) {
      // If the backend rejects the token (maybe it expired after 60 minutes),
      // we force a logout to clear the bad data.
      console.error("Failed to fetch user, token might be expired", error);
      logout(); 
    }
  },
}));

