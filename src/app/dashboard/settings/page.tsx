import { createClient } from "@/supabase/server";
import { redirect } from "next/navigation";
import DashboardNavbar from "@/components/dashboard-navbar";
import AgentSettings from "@/components/agent-settings";

export default async function SettingsPage() {
  const supabase = await createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();

  if (!user) {
    redirect("/sign-in");
  }

  return (
    <div className="min-h-screen bg-background">
      <DashboardNavbar />
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-2">Agent Settings</h1>
        <p className="text-muted-foreground mb-8">
          Configure the connection to your SNMP agent and PDU device
        </p>

        <AgentSettings />
      </div>
    </div>
  );
}
