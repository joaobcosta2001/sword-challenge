import { redirect } from "next/navigation"
import { getUser } from "@/lib/auth"
import WorkspaceContent from "@/components/workspace-content"
import LogoutButton from "@/components/logout-button"

export default async function WorkspacePage() {
  const user = await getUser()

  if (!user) {
    redirect("/")
  }

  return (
    <main className="min-h-screen bg-gray-50">
      <div className="container mx-auto p-4">
        <div className="bg-white rounded-lg shadow-md p-6">
          <h1 className="text-2xl font-bold mb-6">Workspace</h1>
          <div className="flex flex-row flex-grow">
            <p className="mb-4">Welcome, {user}!</p>
            <div className="ml-auto">
              <LogoutButton/>
            </div>
          </div>
          <WorkspaceContent />
        </div>
      </div>
    </main>
  )
}
