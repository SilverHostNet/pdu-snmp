import { createClient } from "../../supabase/server";
import { redirect } from "next/navigation";
import DashboardNavbar from "@/components/dashboard-navbar";
import OutletControl from "@/components/outlet-control";
import OutletHistory from "@/components/outlet-history";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface OutletPageProps {
  params: {
    id: string;
  };
}

export default async function OutletPage({ params }: OutletPageProps) {
  // For storyboard purposes, we'll use sample data instead of fetching from Supabase
  // This avoids authentication issues in the storyboard context

  // Sample outlet data
  const outletData = {
    id: params.id,
    name: `Outlet ${params.id}`,
    state: "on",
    voltage: 120,
    current: 5,
    lastUpdated: new Date().toISOString(),
  };

  return (
    <div className="min-h-screen bg-background">
      <DashboardNavbar />
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-2">{outletData.name}</h1>
        <p className="text-muted-foreground mb-8">
          Monitor and control this outlet
        </p>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <Card className="bg-background">
            <CardHeader>
              <CardTitle>Outlet Status</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                <div className="flex items-center gap-2 mb-4">
                  <div
                    className={`w-4 h-4 rounded-full ${outletData.state === "on" ? "bg-green-500" : "bg-gray-400"}`}
                  ></div>
                  <span className="text-xl font-medium">
                    {outletData.state === "on" ? "ON" : "OFF"}
                  </span>
                </div>

                <div className="grid grid-cols-2 gap-y-4">
                  <div className="text-muted-foreground">Voltage:</div>
                  <div className="font-medium">{outletData.voltage} V</div>

                  <div className="text-muted-foreground">Current:</div>
                  <div className="font-medium">{outletData.current} A</div>

                  <div className="text-muted-foreground">Power:</div>
                  <div className="font-medium">
                    {outletData.voltage * outletData.current} W
                  </div>

                  <div className="text-muted-foreground">Last Updated:</div>
                  <div className="font-medium">
                    {new Date(outletData.lastUpdated).toLocaleString()}
                  </div>
                </div>

                <div className="flex gap-4 pt-4">
                  <OutletControl outlet={outletData} />
                  <OutletHistory outletId={params.id} />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-background">
            <CardHeader>
              <CardTitle>Power Consumption</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-[300px] flex items-center justify-center">
                <p className="text-muted-foreground">
                  Power consumption chart will be displayed here
                </p>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
