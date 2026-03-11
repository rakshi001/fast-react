import { create } from "zustand";
import { projectsApi, type Project } from "@/api/services";

/**
 * ============================================================================
 * STATE MANAGEMENT (Zustand) - Project Store
 * ============================================================================
 * This store holds all the data related to Projects so that any component,
 * like the Sidebar or the Dashboard, can read the project list without
 * needing to fetch the API themselves.
 * ============================================================================
 */

// 1. Defining the "Shape" of our Store
interface ProjectState {
  projects: Project[];               // Array holding all of the user's projects
  activeProject: Project | null;     // The currently selected project in the UI
  isLoading: boolean;                // Is the app currently fetching projects from the backend?
  
  // Actions
  fetchProjects: () => Promise<void>;
  createProject: (data: { title: string; description?: string }) => Promise<void>;
  updateProject: (id: number, data: { title?: string; description?: string }) => Promise<void>;
  deleteProject: (id: number) => Promise<void>;
  setActiveProject: (project: Project | null) => void;
}

// 2. Creating the Store
export const useProjectStore = create<ProjectState>((set) => ({
  projects: [],
  activeProject: null,
  isLoading: false,

  // ACTION: Fetch all projects from the backend
  fetchProjects: async () => {
    set({ isLoading: true });
    try {
      // Calls the Axios wrapper we made in api/services.ts
      const projects = await projectsApi.getAll();
      set({ projects, isLoading: false });
    } catch (error) {
      console.error(error);
      set({ isLoading: false });
    }
  },

  // ACTION: Create a new project
  createProject: async (data) => {
    // 1. Send request to the backend
    const newProject = await projectsApi.create(data);
    
    // 2. Once the backend replies with the newly created Database record, 
    //    append it to our React state so the UI updates instantly!
    set((state) => ({ projects: [...state.projects, newProject] }));
  },

  // ACTION: Update a project's title/description
  updateProject: async (id, data) => {
    const updated = await projectsApi.update(id, data);
    
    // Loop through our project array. If the ID matches, swap it with the updated version.
    set((state) => ({
      projects: state.projects.map((p) => (p.id === id ? updated : p)),
    }));
  },

  // ACTION: Delete a project
  deleteProject: async (id) => {
    // 1. Tell backend to delete
    await projectsApi.delete(id);
    
    // 2. Remove it from React state by filtering it out
    set((state) => ({
      projects: state.projects.filter((p) => p.id !== id),
      // If the project we just deleted was the "Active" one, clear the active selection.
      activeProject: state.activeProject?.id === id ? null : state.activeProject,
    }));
  },

  // ACTION: When a user clicks a project in the sidebar, update the state.
  setActiveProject: (project) => set({ activeProject: project }),
}));
