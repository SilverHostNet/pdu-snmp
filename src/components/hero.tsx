import Link from "next/link";
import {
  ArrowUpRight,
  Check,
  Power,
  Activity,
  Shield,
  History,
} from "lucide-react";

export default function Hero() {
  return (
    <div className="relative overflow-hidden bg-white">
      {/* Background gradient */}
      <div className="absolute inset-0 bg-gradient-to-br from-blue-50 via-white to-blue-50 opacity-70" />

      <div className="relative pt-24 pb-32 sm:pt-32 sm:pb-40">
        <div className="container mx-auto px-4">
          <div className="text-center max-w-4xl mx-auto">
            <h1 className="text-5xl sm:text-6xl font-bold text-gray-900 mb-8 tracking-tight">
              Smart{" "}
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-green-600">
                PDU Control
              </span>{" "}
              System
            </h1>

            <p className="text-xl text-gray-600 mb-12 max-w-2xl mx-auto leading-relaxed">
              Monitor and control your Raritan PDU outlets with our advanced
              SNMP management system. Real-time status updates, historical data,
              and secure remote control.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
              <Link
                href="/dashboard"
                className="inline-flex items-center px-8 py-4 text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors text-lg font-medium"
              >
                Access Dashboard
                <ArrowUpRight className="ml-2 w-5 h-5" />
              </Link>

              <Link
                href="#features"
                className="inline-flex items-center px-8 py-4 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors text-lg font-medium"
              >
                View Features
              </Link>
            </div>

            <div className="mt-16 flex flex-col sm:flex-row items-center justify-center gap-8 text-sm text-gray-600">
              <div className="flex items-center gap-2">
                <Power className="w-5 h-5 text-green-500" />
                <span>Remote Power Control</span>
              </div>
              <div className="flex items-center gap-2">
                <Activity className="w-5 h-5 text-green-500" />
                <span>Real-time Monitoring</span>
              </div>
              <div className="flex items-center gap-2">
                <History className="w-5 h-5 text-green-500" />
                <span>Historical Data Analysis</span>
              </div>
              <div className="flex items-center gap-2">
                <Shield className="w-5 h-5 text-green-500" />
                <span>Secure Authentication</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
