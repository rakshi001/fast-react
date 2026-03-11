import axios from "axios";

/**
 * ============================================================================
 * API CLIENT CONFIGURATION (Axios)
 * ============================================================================
 * What is Axios? 
 * It's a library used to make HTTP requests (GET, POST, PUT, DELETE) to our backend.
 * 
 * Why create an "instance"?
 * Instead of typing out "http://localhost:8000" in every single file, we create
 * a base client here. We also tell it that we are sending JSON data by default.
 */
export const apiClient = axios.create({
  // The base URL for all requests. 
  // It checks for an environment variable first, but defaults to our local FastAPI server port.
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000",
  headers: {
    "Content-Type": "application/json",
  },
});

/**
 * INTERCEPTORS
 * Think of interceptors like a security checkpoint that every request has to pass through 
 * BEFORE it leaves the browser and hits our backend.
 * 
 * Why do we need this?
 * Our backend routes (like creating a project) are protected. They require a valid JWT token
 * to prove "who" is making the request.
 * Instead of manually attaching the token to every single request in our codebase, 
 * this interceptor automatically intercepts the request, grabs the token from the browser's 
 * LocalStorage, and forcefully injects it into the Headers.
 */
apiClient.interceptors.request.use(
  (config) => {
    // 1. Look inside the browser's "Local Storage" for our saved token
    const token = localStorage.getItem("kw_token");
    
    // 2. If a token exists, attach it to the Authorization header
    // The format MUST be "Bearer <token>" because that's what FastAPI's OAuth2 expects.
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    // 3. Send the modified request on its way
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);
