import { Outlet, Navigate } from "react-router-dom";
import { useAuthStore } from "@/store/useAuthStore";
import { Button } from "@/components/ui/button";
import { LogOut, Folder, User } from "lucide-react";
import { useProjectStore } from "@/store/useProjectStore";

/**
 * ============================================================================
 * REACT COMPONENT - Layout Wrapper
 * ============================================================================
 * Notice how both the Dashboard and future pages (like Settings) share the 
 * exact same Navbar and Sidebar? 
 * 
 * Instead of copy-pasting the Sidebar code into every single page, React Router
 * uses this Layout component as a "Wrapper". It renders the common UI (header, sidebar)
 * and uses the special `<Outlet />` component to inject the specific page content inside.
 * ============================================================================
 */
export default function Layout() {
  const { isAuthenticated, user, logout } = useAuthStore();
  const { projects, activeProject, setActiveProject } = useProjectStore();

  // --- ROUTE PROTECTION ---
  // If someone manually types "http://localhost:5173/" but they aren't logged in,
  // we catch them here and forcefully redirect them to the Login page.
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return (
    <div className="flex min-h-screen w-full flex-col bg-muted/40">
      
      {/* --- HEADER (Navbar) --- */}
      <header className="sticky top-0 z-30 flex h-14 items-center gap-4 border-b bg-background px-4 sm:static sm:h-auto sm:border-0 sm:bg-transparent sm:px-6 py-3 justify-between">
        <div className="flex items-center gap-2 font-semibold">
          <div className="h-8 w-8 rounded-full bg-primary flex items-center justify-center text-primary-foreground">
            KW
          </div>
          <span>Knowledge Workspace</span>
        </div>
        <div className="flex items-center gap-4">
          <div className="text-sm font-medium flex items-center gap-2">
            <User className="h-4 w-4" />
            {user?.full_name || user?.email}
          </div>
          <Button variant="ghost" size="icon" onClick={() => logout()} title="Logout">
            <LogOut className="h-5 w-5" />
          </Button>
        </div>
      </header>

      <div className="flex flex-1 overflow-hidden">
        
        {/* --- SIDEBAR (Projects List) --- */}
        <aside className="hidden w-64 flex-col border-r bg-background sm:flex overflow-y-auto">
          <div className="p-4 border-b">
            <h2 className="text-lg font-semibold tracking-tight">Projects</h2>
          </div>
          <nav className="grid items-start px-2 text-sm font-medium lg:px-4 py-4 gap-1">
            {/* Loop through projects from our Zustand store and create a clickable button for each */}
            {projects.map((project) => (
              <button
                key={project.id}
                onClick={() => setActiveProject(project)}
                className={`flex items-center gap-3 rounded-lg px-3 py-2 transition-all hover:text-primary ${
                  activeProject?.id === project.id ? "bg-muted text-primary" : "text-muted-foreground"
                }`}
              >
                <Folder className="h-4 w-4" />
                <span className="truncate flex-1 text-left">{project.title}</span>
              </button>
            ))}
            
            {/* Show a placeholder message if the user has 0 projects yet */}
            {projects.length === 0 && (
              <div className="text-center text-muted-foreground p-4 text-sm mt-4">
                No projects yet. Create one!
              </div>
            )}
          </nav>
        </aside>

        {/* --- MAIN CONTENT AREA --- */}
        <main className="flex flex-1 flex-col gap-4 p-4 lg:gap-6 lg:p-6 overflow-y-auto bg-background rounded-tl-xl border-t border-l shadow-sm">
          {/* 
            This <Outlet /> is the magic piece! 
            If the URL is '/', React Router replaces this Outlet with `<Dashboard />`.
            If the URL was '/settings', it would inject `<Settings />` right here instead.
          */}
          <Outlet />
        </main>
        
      </div>
    </div>
  );
}
