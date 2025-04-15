import { NextResponse } from "next/server"
import type { NextRequest } from "next/server"

export function middleware(request: NextRequest) {
  const path = request.nextUrl.pathname

  // Define protected routes
  const isWorkspacePath = path === "/workspace" || path.startsWith("/workspace/")

  // Get the user cookie
  const userCookie = request.cookies.get("token")?.value

  console.log("User cookie:", userCookie)

  // If trying to access workspace without being logged in, redirect to login
  if (isWorkspacePath && !userCookie) {
    return NextResponse.redirect(new URL("/", request.url))
  }

  // If already logged in and trying to access login page, redirect to workspace
  if (path === "/" && userCookie) {
    return NextResponse.redirect(new URL("/workspace", request.url))
  }

  return NextResponse.next()
}

// See "Matching Paths" below to learn more
export const config = {
  matcher: ["/", "/workspace/:path*"],
}
