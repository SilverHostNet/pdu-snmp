"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { createClient } from "@supabase/supabase-js";
import { useToast } from "@/components/ui/use-toast";

export default function AgentSettings() {
  const [agentHost, setAgentHost] = useState("localhost");
  const [agentPort, setAgentPort] = useState("5000");
  const [pduHost, setPduHost] = useState("192.168.1.100");
  const [snmpCommunity, setSnmpCommunity] = useState("public");
  const [snmpVersion, setSnmpVersion] = useState("2c");
  const [isSaving, setIsSaving] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const { toast } = useToast();

  // Initialize Supabase client
  const supabase = createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL || "",
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || "",
  );

  useEffect(() => {
    // Load settings from Supabase
    const loadSettings = async () => {
      try {
        const { data: agents, error: agentsError } = await supabase
          .from("agents")
          .select("*")
          .limit(1)
          .single();

        if (agentsError) throw agentsError;

        if (agents) {
          setAgentHost(agents.host);
          setAgentPort(agents.port.toString());
          setIsConnected(agents.status === "connected");

          // Get PDU device info
          const { data: devices, error: devicesError } = await supabase
            .from("devices")
            .select("*")
            .eq("agent_id", agents.id)
            .limit(1)
            .single();

          if (!devicesError && devices) {
            setPduHost(devices.host);
            setSnmpCommunity(devices.snmp_community);
            setSnmpVersion(devices.snmp_version);
          }
        }
      } catch (error) {
        console.error("Error loading settings:", error);
        // Use default values if no settings found
      }
    };

    loadSettings();
  }, [supabase]);

  const testConnection = async () => {
    setIsSaving(true);
    try {
      const agentApiUrl = `http://${agentHost}:${agentPort}`;
      const response = await fetch(`${agentApiUrl}/healthz`, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to connect to agent: ${response.statusText}`);
      }

      const data = await response.json();
      if (data.status === "ok") {
        setIsConnected(true);
        toast({
          title: "Connection Successful",
          description: "Successfully connected to the SNMP agent",
        });
      } else {
        throw new Error("Agent returned unexpected response");
      }
    } catch (error) {
      console.error("Error connecting to agent:", error);
      setIsConnected(false);
      toast({
        title: "Connection Failed",
        description: "Failed to connect to the SNMP agent",
        variant: "destructive",
      });
    } finally {
      setIsSaving(false);
    }
  };

  const saveSettings = async () => {
    setIsSaving(true);
    try {
      // First check if we have an existing agent
      const { data: existingAgent, error: fetchError } = await supabase
        .from("agents")
        .select("id")
        .limit(1)
        .single();

      let agentId;

      if (fetchError || !existingAgent) {
        // Create new agent
        const { data: newAgent, error: createError } = await supabase
          .from("agents")
          .insert({
            name: "Default Agent",
            host: agentHost,
            port: parseInt(agentPort),
            status: isConnected ? "connected" : "unknown",
          })
          .select()
          .single();

        if (createError) throw createError;
        agentId = newAgent.id;
      } else {
        // Update existing agent
        agentId = existingAgent.id;
        const { error: updateError } = await supabase
          .from("agents")
          .update({
            host: agentHost,
            port: parseInt(agentPort),
            status: isConnected ? "connected" : "unknown",
            updated_at: new Date().toISOString(),
          })
          .eq("id", agentId);

        if (updateError) throw updateError;
      }

      // Now handle the device
      const { data: existingDevice, error: deviceFetchError } = await supabase
        .from("devices")
        .select("id")
        .eq("agent_id", agentId)
        .limit(1)
        .single();

      if (deviceFetchError || !existingDevice) {
        // Create new device
        const { error: deviceCreateError } = await supabase
          .from("devices")
          .insert({
            name: "Default PDU",
            host: pduHost,
            snmp_community: snmpCommunity,
            snmp_version: snmpVersion,
            agent_id: agentId,
          });

        if (deviceCreateError) throw deviceCreateError;
      } else {
        // Update existing device
        const { error: deviceUpdateError } = await supabase
          .from("devices")
          .update({
            host: pduHost,
            snmp_community: snmpCommunity,
            snmp_version: snmpVersion,
            updated_at: new Date().toISOString(),
          })
          .eq("id", existingDevice.id);

        if (deviceUpdateError) throw deviceUpdateError;
      }

      toast({
        title: "Settings Saved",
        description: "Agent and PDU settings have been updated",
      });
    } catch (error) {
      console.error("Error saving settings:", error);
      toast({
        title: "Error",
        description: "Failed to save settings",
        variant: "destructive",
      });
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <Card className="w-full max-w-2xl mx-auto bg-background">
      <CardHeader>
        <CardTitle>Agent Settings</CardTitle>
        <CardDescription>
          Configure the connection to your SNMP agent and PDU device
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="space-y-4">
          <div>
            <h3 className="text-lg font-medium">Agent Connection</h3>
            <p className="text-sm text-muted-foreground mb-4">
              Configure the connection to your local SNMP agent
            </p>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="agentHost">Agent Host</Label>
              <Input
                id="agentHost"
                value={agentHost}
                onChange={(e) => setAgentHost(e.target.value)}
                placeholder="localhost"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="agentPort">Agent Port</Label>
              <Input
                id="agentPort"
                value={agentPort}
                onChange={(e) => setAgentPort(e.target.value)}
                placeholder="5000"
              />
            </div>
          </div>

          <div className="flex justify-end">
            <Button
              variant="outline"
              onClick={testConnection}
              disabled={isSaving}
            >
              Test Connection
            </Button>
          </div>

          <div className="flex items-center gap-2">
            <div
              className={`w-3 h-3 rounded-full ${isConnected ? "bg-green-500" : "bg-red-500"}`}
            ></div>
            <span className="text-sm">
              {isConnected ? "Connected" : "Not Connected"}
            </span>
          </div>
        </div>

        <div className="space-y-4">
          <div>
            <h3 className="text-lg font-medium">PDU Configuration</h3>
            <p className="text-sm text-muted-foreground mb-4">
              Configure the connection to your PDU device
            </p>
          </div>

          <div className="space-y-2">
            <Label htmlFor="pduHost">PDU IP Address</Label>
            <Input
              id="pduHost"
              value={pduHost}
              onChange={(e) => setPduHost(e.target.value)}
              placeholder="192.168.1.100"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="snmpCommunity">SNMP Community</Label>
              <Input
                id="snmpCommunity"
                value={snmpCommunity}
                onChange={(e) => setSnmpCommunity(e.target.value)}
                placeholder="public"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="snmpVersion">SNMP Version</Label>
              <Input
                id="snmpVersion"
                value={snmpVersion}
                onChange={(e) => setSnmpVersion(e.target.value)}
                placeholder="2c"
              />
            </div>
          </div>
        </div>
      </CardContent>
      <CardFooter className="flex justify-end">
        <Button onClick={saveSettings} disabled={isSaving}>
          {isSaving ? "Saving..." : "Save Settings"}
        </Button>
      </CardFooter>
    </Card>
  );
}
