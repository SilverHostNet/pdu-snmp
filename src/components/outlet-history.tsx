"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import { useToast } from "@/components/ui/use-toast";

interface OutletHistoryProps {
  outletId: string;
}

interface ReadingData {
  timestamp: string;
  voltage: number;
  current: number;
  power: number;
  state: string;
}

export default function OutletHistory({ outletId }: OutletHistoryProps) {
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [historyData, setHistoryData] = useState<ReadingData[]>([]);
  const { toast } = useToast();
  const agentApiUrl =
    process.env.NEXT_PUBLIC_AGENT_API_URL || "https://pdu.beardsys.com:5000";

  const fetchHistory = async () => {
    setLoading(true);
    try {
      const response = await fetch(
        `${agentApiUrl}/outlets/${outletId}/history?limit=100`,
      );

      if (!response.ok) {
        throw new Error(`Failed to fetch history: ${response.statusText}`);
      }

      const data = await response.json();

      // Transform data for the chart
      const formattedData = data.map((reading: any) => ({
        timestamp: new Date(reading.created_at).toLocaleString(),
        voltage: reading.voltage || 0,
        current: reading.current || 0,
        power: (reading.voltage || 0) * (reading.current || 0),
        state: reading.state,
      }));

      setHistoryData(formattedData);
    } catch (error) {
      console.error("Error fetching outlet history:", error);
      toast({
        title: "Error",
        description: "Failed to fetch outlet history",
        variant: "destructive",
      });

      // Use sample data if API is not available
      const sampleData = Array.from({ length: 24 }, (_, i) => {
        const date = new Date();
        date.setHours(date.getHours() - (24 - i));
        return {
          timestamp: date.toLocaleString(),
          voltage: 120,
          current: 3 + Math.random() * 2,
          power: 120 * (3 + Math.random() * 2),
          state: "on",
        };
      });
      setHistoryData(sampleData);
    } finally {
      setLoading(false);
    }
  };

  const handleOpenChange = (newOpen: boolean) => {
    setOpen(newOpen);
    if (newOpen) {
      fetchHistory();
    }
  };

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogTrigger asChild>
        <Button variant="outline">View History</Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[800px] max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Outlet {outletId} History</DialogTitle>
        </DialogHeader>

        {loading ? (
          <div className="flex justify-center items-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
          </div>
        ) : (
          <div className="space-y-6">
            <div className="h-[300px]">
              <h3 className="text-sm font-medium mb-2">
                Power Consumption (W)
              </h3>
              <ResponsiveContainer width="100%" height="100%">
                <LineChart
                  data={historyData}
                  margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis
                    dataKey="timestamp"
                    tick={{ fontSize: 12 }}
                    interval={Math.ceil(historyData.length / 8)}
                  />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="power"
                    stroke="#8884d8"
                    activeDot={{ r: 8 }}
                    name="Power (W)"
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>

            <div className="h-[300px]">
              <h3 className="text-sm font-medium mb-2">Current (A)</h3>
              <ResponsiveContainer width="100%" height="100%">
                <LineChart
                  data={historyData}
                  margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis
                    dataKey="timestamp"
                    tick={{ fontSize: 12 }}
                    interval={Math.ceil(historyData.length / 8)}
                  />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="current"
                    stroke="#82ca9d"
                    name="Current (A)"
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}
