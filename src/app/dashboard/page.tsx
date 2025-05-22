import { createClient } from "@/supabase/server";
import { redirect } from "next/navigation";
import DashboardNavbar from "@/components/dashboard-navbar";
import OutletList from "@/components/outlet-list";

export default async function DashboardPage() {
  // For storyboard purposes, we'll skip authentication check
  // In a real app, we would check for authentication here

  return (
    <div className="min-h-screen bg-background">
      <DashboardNavbar />
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-2">PDU Outlet Control</h1>
        <p className="text-muted-foreground mb-8">
          Monitor and control your PDU outlets from this dashboard
        </p>

        <OutletList />
      </div>
    </div>
  );
}
