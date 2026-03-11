import { create } from "zustand";
import { notesApi, type Note } from "@/api/services";

/**
 * ============================================================================
 * STATE MANAGEMENT (Zustand) - Note Store
 * ============================================================================
 * Similar to the Project Store, this manages the Notes for whatever project
 * is currently active.
 * ============================================================================
 */

interface NoteState {
  notes: Note[];
  isLoading: boolean;
  
  // Actions
  fetchNotes: (projectId: number) => Promise<void>;
  createNote: (projectId: number, data: { title: string; content?: string }) => Promise<void>;
  updateNote: (id: number, data: { title?: string; content?: string }) => Promise<void>;
  deleteNote: (id: number) => Promise<void>;
}

export const useNoteStore = create<NoteState>((set) => ({
  notes: [],
  isLoading: false,

  // Fetches notes. Note that it requires a `projectId` because notes belong to projects.
  fetchNotes: async (projectId) => {
    set({ isLoading: true });
    try {
      const notes = await notesApi.getAllByProject(projectId);
      set({ notes, isLoading: false });
    } catch (error) {
      console.error(error);
      set({ isLoading: false });
    }
  },

  createNote: async (projectId, data) => {
    const newNote = await notesApi.create(projectId, data);
    set((state) => ({ notes: [...state.notes, newNote] }));
  },

  updateNote: async (id, data) => {
    const updated = await notesApi.update(id, data);
    set((state) => ({
      notes: state.notes.map((n) => (n.id === id ? updated : n)),
    }));
  },

  deleteNote: async (id) => {
    await notesApi.delete(id);
    set((state) => ({
      notes: state.notes.filter((n) => n.id !== id),
    }));
  },
}));
