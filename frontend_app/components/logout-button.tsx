"use client"

import { LogOut } from "lucide-react";
import { Button } from "./ui/button";
import { logout } from "@/lib/auth";
import { useRouter } from "next/navigation";


export default function LogoutButton() {
        
    const router = useRouter()

    const handleLogout = async () => {
        await logout()
        router.push("/")
    }


    return(
        <Button
            variant="ghost"
            size="icon"
            onClick={handleLogout}
            className={"text-gray-500 hover:text-primary hover:bg-primary/10 "}
        >
            <LogOut size={20} />
            <span className="sr-only">Logout</span>
        </Button>
    )

    
}