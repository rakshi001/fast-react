import { useEffect, useState } from "react";
import { useAuthStore } from "@/store/useAuthStore";
import { useProjectStore } from "@/store/useProjectStore";
import { useNoteStore } from "@/store/useNoteStore";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { PlusCircle, Save, Trash2 } from "lucide-react";

/**
 * ============================================================================
 * REACT COMPONENT - Main Dashboard
 * ============================================================================
 * This is the heaviest component. It ties together users, projects, and notes.
 * It listens to 3 different Zustand stores simultaneously.
 * ============================================================================
 */
export default function Dashboard() {
  // --- ZUSTAND STORE CONNECTIONS ---
  // Connecting to our global stores lets this component map over objects directly
  // and trigger actions to update the backend.
  const { user } = useAuthStore();
  const { activeProject, fetchProjects, createProject, deleteProject } = useProjectStore();
  const { notes, isLoading: notesLoading, fetchNotes, createNote, updateNote, deleteNote } = useNoteStore();

  // --- LOCAL UI STATE ---
  // Temporary state for the input fields when users are typing before hitting "Submit"
  const [newProjectTitle, setNewProjectTitle] = useState("");
  const [newNoteTitle, setNewNoteTitle] = useState("");
  const [newNoteContent, setNewNoteContent] = useState("");
  // Tracks which specific note (by ID) is currently turned into an editable textarea
  const [editingNoteId, setEditingNoteId] = useState<number | null>(null);

  // --- LIFECYCLE HOOKS ---
  // This useEffect fires ONCE as soon as the Dashboard loads.
  // It calls the backend to grab the user's project list.
  useEffect(() => {
    fetchProjects();
  }, [fetchProjects]);

  // This useEffect fires EVERY TIME the `activeProject` changes.
  // If the user clicks a different project in the sidebar, this tells the Note Store
  // to fetch the notes corresponding to that specific Project ID.
  useEffect(() => {
    if (activeProject) {
      fetchNotes(activeProject.id);
    }
  }, [activeProject, fetchNotes]);

  // --- FORM HANDLERS ---
  const handleCreateProject = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newProjectTitle.trim()) return;
    await createProject({ title: newProjectTitle });
    setNewProjectTitle(""); // Reset the input box
  };

  const handleCreateNote = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!activeProject || (!newNoteTitle.trim() && !newNoteContent.trim())) return;
    await createNote(activeProject.id, { title: newNoteTitle || "Untitled Note", content: newNoteContent });
    setNewNoteTitle("");
    setNewNoteContent("");
  };

  const handleUpdateNote = async (noteId: number, title: string, content: string) => {
    await updateNote(noteId, { title, content });
    setEditingNoteId(null); // Turn off 'edit mode' after saving
  };

  // --- RENDER BLOCK 1: NO ACTIVE PROJECT ---
  // If the user hasn't selected a project yet, or has 0 projects, show a welcome screen.
  if (!activeProject) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-center p-8">
        <h2 className="text-2xl font-bold tracking-tight">Welcome, {user?.full_name || user?.email}!</h2>
        <p className="text-muted-foreground mt-2 mb-8">
          Select a project from the sidebar or create a new one to start taking notes.
        </p>
        <Card className="w-full max-w-sm">
          <CardHeader>
            <CardTitle>Create Project</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleCreateProject} className="flex flex-col gap-4">
              <Input
                placeholder="Project Name..."
                value={newProjectTitle}
                onChange={(e) => setNewProjectTitle(e.target.value)}
              />
              {/* Disable the button if the input is completely empty */}
              <Button type="submit" disabled={!newProjectTitle.trim()}>
                <PlusCircle className="w-4 h-4 mr-2" />
                Create Project
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>
    );
  }

  // --- RENDER BLOCK 2: PROJECT VIEW ---
  // The user has selected an active project. Show its notes.
  return (
    <div className="flex flex-col h-full gap-6">
      
      {/* Top Header Row (Project Title + Delete Project Button) */}
      <div className="flex items-center justify-between border-b pb-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">{activeProject.title}</h1>
          {activeProject.description && <p className="text-muted-foreground mt-1">{activeProject.description}</p>}
        </div>
        <Button variant="destructive" size="sm" onClick={() => deleteProject(activeProject.id)}>
          <Trash2 className="w-4 h-4 mr-2" />
          Delete Project
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 h-full pb-8">
        {/* Left Side: NOTES LIST */}
        <div className="md:col-span-2 flex flex-col gap-4 overflow-y-auto">
          {notesLoading ? (
            <div className="text-muted-foreground">Loading notes...</div>
          ) : notes.length === 0 ? (
            <div className="p-8 text-center border rounded-lg bg-muted/20 border-dashed">
              <p className="text-muted-foreground">No notes found. Create your first note!</p>
            </div>
          ) : (
            // Loop through the notes array inherited from the Zustand store
            notes.map((note) => (
              <Card key={note.id} className="w-full">
                
                {/* CONDITIONAL RENDER: "Edit Mode" vs "View Mode" */}
                {editingNoteId === note.id ? (
                  // ----- EDIT MODE UI -----
                  // This renders input fields so you can modify the text
                  <form
                    onSubmit={(e) => {
                      e.preventDefault();
                      // Grab the data directly from the DOM form elements
                      const formData = new FormData(e.target as HTMLFormElement);
                      handleUpdateNote(
                        note.id,
                        formData.get("title") as string,
                        formData.get("content") as string
                      );
                    }}
                  >
                    <CardHeader className="py-3">
                      <Input name="title" defaultValue={note.title} className="font-bold text-lg" required />
                    </CardHeader>
                    <CardContent className="pb-3 flex flex-col gap-3">
                      <Textarea name="content" defaultValue={note.content} className="min-h-[100px]" />
                      <div className="flex justify-end gap-2">
                        <Button variant="ghost" size="sm" type="button" onClick={() => setEditingNoteId(null)}>
                          Cancel
                        </Button>
                        <Button size="sm" type="submit">
                          <Save className="w-4 h-4 mr-2" />
                          Save
                        </Button>
                      </div>
                    </CardContent>
                  </form>
                ) : (
                  // ----- VIEW MODE UI -----
                  // This just displays the text normally
                  <>
                    <CardHeader className="py-3 flex flex-row items-center justify-between">
                      <CardTitle className="text-lg">{note.title}</CardTitle>
                      <div className="flex gap-2">
                        {/* Switch to edit mode on click by updating local UI state */}
                        <Button variant="outline" size="sm" onClick={() => setEditingNoteId(note.id)}>
                          Edit
                        </Button>
                        <Button variant="destructive" size="sm" onClick={() => deleteNote(note.id)}>
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </CardHeader>
                    <CardContent className="pb-4">
                      <p className="whitespace-pre-wrap text-sm">{note.content}</p>
                    </CardContent>
                  </>
                )}
                
              </Card>
            ))
          )}
        </div>

        {/* Right Side: CREATE NEW NOTE FORM */}
        <div className="flex flex-col">
          <Card className="sticky top-0">
            <CardHeader>
              <CardTitle>New Note</CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleCreateNote} className="flex flex-col gap-4">
                <Input
                  placeholder="Note Title"
                  value={newNoteTitle}
                  onChange={(e) => setNewNoteTitle(e.target.value)}
                  required
                />
                <Textarea
                  placeholder="Note content..."
                  value={newNoteContent}
                  onChange={(e) => setNewNoteContent(e.target.value)}
                  className="min-h-[150px]"
                />
                <Button type="submit" className="w-full">
                  <PlusCircle className="w-4 h-4 mr-2" />
                  Add Note
                </Button>
              </form>
            </CardContent>
          </Card>
        </div>
        
      </div>
    </div>
  );
}
