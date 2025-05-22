"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { createClient } from "@supabase/supabase-js";
import OutletControl from "@/components/outlet-control";
import { useToast } from "@/components/ui/use-toast";

interface Outlet {
  id: string;
  name: string;
  state: string;
  voltage: number;
  current: number;
  lastUpdated: string;
}

export default function OutletList() {
  const [outlets, setOutlets] = useState<Outlet[]>([]);
  const [loading, setLoading] = useState(true);
  const { toast } = useToast();
  const agentApiUrl =
    process.env.NEXT_PUBLIC_AGENT_API_URL || "https://pdu.beardsys.com:5000";

  // Initialize Supabase client
  const supabase = createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL || "",
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || "",
  );

  useEffect(() => {
    // Fetch initial outlet data
    const fetchOutlets = async () => {
      try {
        const response = await fetch(`${agentApiUrl}/outlets`, {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
          },
          mode: "cors",
        });
        if (!response.ok) {
          throw new Error(`Failed to fetch outlets: ${response.statusText}`);
        }
        const data = await response.json();
        setOutlets(data.outlets || []);
      } catch (error) {
        console.error("Error fetching outlets:", error);
        toast({
          title: "Error",
          description: "Failed to fetch outlet data",
          variant: "destructive",
        });
        // Use sample data if API is not available
        setOutlets([
          {
            id: "1",
            name: "Outlet 1",
            state: "on",
            voltage: 120,
            current: 5,
            lastUpdated: new Date().toISOString(),
          },
          {
            id: "2",
            name: "Outlet 2",
            state: "off",
            voltage: 0,
            current: 0,
            lastUpdated: new Date().toISOString(),
          },
          {
            id: "3",
            name: "Outlet 3",
            state: "on",
            voltage: 120,
            current: 3,
            lastUpdated: new Date().toISOString(),
          },
        ]);
      } finally {
        setLoading(false);
      }
    };

    fetchOutlets();

    // Set up realtime subscription for outlet changes
    const subscription = supabase
      .channel("outlet_changes")
      .on(
        "postgres_changes",
        { event: "UPDATE", schema: "public", table: "outlet_readings" },
        (payload) => {
          // Update the outlet data when changes occur
          fetchOutlets();
        },
      )
      .subscribe();

    // Clean up subscription on unmount
    return () => {
      subscription.unsubscribe();
    };
  }, [agentApiUrl, toast]);

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {outlets.map((outlet) => (
        <Card key={outlet.id} className="bg-background">
          <CardHeader className="pb-2">
            <CardTitle className="text-lg flex items-center gap-2">
              <div
                className={`w-3 h-3 rounded-full ${outlet.state === "on" ? "bg-green-500" : "bg-gray-400"}`}
              ></div>
              {outlet.name}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-2 text-sm">
                <div className="text-muted-foreground">Status:</div>
                <div className="font-medium">{outlet.state.toUpperCase()}</div>

                <div className="text-muted-foreground">Voltage:</div>
                <div className="font-medium">{outlet.voltage} V</div>

                <div className="text-muted-foreground">Current:</div>
                <div className="font-medium">{outlet.current} A</div>

                <div className="text-muted-foreground">Power:</div>
                <div className="font-medium">
                  {(outlet.voltage * outlet.current).toFixed(1)} W
                </div>
              </div>

              <div className="pt-2">
                <OutletControl outlet={outlet} />
              </div>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
