"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Power, RotateCw } from "lucide-react";
import { useToast } from "@/components/ui/use-toast";

interface OutletProps {
  outlet: {
    id: string;
    name: string;
    state: string;
    voltage?: number;
    current?: number;
    lastUpdated?: string;
  };
}

export default function OutletControl({ outlet }: OutletProps) {
  const [isLoading, setIsLoading] = useState(false);
  const { toast } = useToast();
  const agentApiUrl =
    process.env.NEXT_PUBLIC_AGENT_API_URL || "https://pdu.beardsys.com:5000";

  const toggleOutlet = async () => {
    setIsLoading(true);
    try {
      console.log(
        `Toggling outlet ${outlet.id} at: ${agentApiUrl}/outlets/${outlet.id}/toggle`,
      );
      const response = await fetch(
        `${agentApiUrl}/outlets/${outlet.id}/toggle`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          mode: "cors",
          cache: "no-cache",
        },
      );

      if (!response.ok) {
        throw new Error(`Failed to toggle outlet: ${response.statusText}`);
      }

      const data = await response.json();

      toast({
        title: "Outlet toggled",
        description: `${outlet.name} is now ${data.state}`,
        variant: data.state === "on" ? "default" : "destructive",
      });
    } catch (error) {
      console.error("Error toggling outlet:", error);
      toast({
        title: "Error",
        description: `Failed to toggle ${outlet.name}`,
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const cycleOutlet = async () => {
    setIsLoading(true);
    try {
      console.log(
        `Cycling outlet ${outlet.id} at: ${agentApiUrl}/outlets/${outlet.id}/cycle`,
      );
      const response = await fetch(
        `${agentApiUrl}/outlets/${outlet.id}/cycle`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          mode: "cors",
          cache: "no-cache",
        },
      );

      if (!response.ok) {
        throw new Error(`Failed to cycle outlet: ${response.statusText}`);
      }

      const data = await response.json();

      toast({
        title: "Outlet cycled",
        description: `${outlet.name} has been power cycled`,
      });
    } catch (error) {
      console.error("Error cycling outlet:", error);
      toast({
        title: "Error",
        description: `Failed to cycle ${outlet.name}`,
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex gap-2">
      <Button
        variant={outlet.state === "on" ? "default" : "outline"}
        size="sm"
        onClick={toggleOutlet}
        disabled={isLoading}
      >
        <Power className="h-4 w-4 mr-1" />
        {outlet.state === "on" ? "Turn Off" : "Turn On"}
      </Button>
      <Button
        variant="outline"
        size="sm"
        onClick={cycleOutlet}
        disabled={isLoading || outlet.state === "off"}
      >
        <RotateCw className="h-4 w-4 mr-1" />
        Cycle
      </Button>
    </div>
  );
}
