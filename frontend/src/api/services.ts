import { apiClient } from "./client";

/**
 * ============================================================================
 * API SERVICES LAYER
 * ============================================================================
 * This file acts as a clean "wrapper" around all our backend endpoints.
 * 
 * Why do we do this?
 * 1. Reusability: If we need to fetch projects in 3 different components, 
 *    we don't want to write `apiClient.get("/projects")` 3 times.
 * 2. Maintenance: If the backend URL changes from `/projects` to `/v1/projects`, 
 *    we only have to fix it here in one place, instead of hunting through all UI files.
 * ============================================================================
 */

export const authApi = {
  // Contacts POST /auth/login. Takes email/password and returns the JWT token.
  login: async (credentials: Record<string, string>) => {
    const response = await apiClient.post("/auth/login", credentials);
    return response.data;
  },
  
  // Contacts POST /auth/register. Creates a new user in the database.
  register: async (data: Record<string, string>) => {
    const response = await apiClient.post("/auth/register", data);
    return response.data;
  },
};

// Typescript Interfaces: 
// These act as "Contracts" guaranteeing what data shape we expect from the backend.
export interface Project {
  id: number;
  title: string;
  description?: string;
  created_at: string;
}

export const projectsApi = {
  // GET /projects -> Fetches all projects belonging to the logged-in user
  getAll: async () => {
    const response = await apiClient.get<Project[]>("/projects/");
    return response.data;
  },
  
  // POST /projects -> Creates a new project
  create: async (data: { title: string; description?: string }) => {
    const response = await apiClient.post<Project>("/projects/", data);
    return response.data;
  },
  
  // PUT /projects/{id} -> Updates an existing project
  update: async (id: number, data: { title?: string; description?: string }) => {
    const response = await apiClient.put<Project>(`/projects/${id}`, data);
    return response.data;
  },
  
  // DELETE /projects/{id} -> Deletes a project
  delete: async (id: number) => {
    await apiClient.delete(`/projects/${id}`);
  },
};

export interface Note {
  id: number;
  title: string;
  content: string;
  project_id: number;
  created_at: string;
  updated_at: string;
}

export const notesApi = {
  // Notice we pass the projectId in the URL path, matching our backend's router setup!
  getAllByProject: async (projectId: number) => {
    const response = await apiClient.get<Note[]>(`/projects/${projectId}/notes`);
    return response.data;
  },
  
  create: async (projectId: number, data: { title: string; content?: string }) => {
    const response = await apiClient.post<Note>(`/projects/${projectId}/notes`, data);
    return response.data;
  },
  
  update: async (id: number, data: { title?: string; content?: string }) => {
    const response = await apiClient.put<Note>(`/notes/${id}`, data);
    return response.data;
  },
  
  delete: async (id: number) => {
    await apiClient.delete(`/notes/${id}`);
  },
};
