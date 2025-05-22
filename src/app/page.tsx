import Footer from "@/components/footer";
import Hero from "@/components/hero";
import Navbar from "@/components/navbar";
import {
  ArrowUpRight,
  Power,
  Activity,
  Database,
  LineChart,
  Shield,
  Zap,
  Server,
  Wifi,
} from "lucide-react";
import { createClient } from "../../supabase/server";

export default async function Home() {
  const supabase = await createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();

  return (
    <div className="min-h-screen bg-gradient-to-b from-white to-gray-50">
      <Navbar />
      <Hero />

      {/* Features Section */}
      <section id="features" className="py-24 bg-white">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold mb-4">Key Features</h2>
            <p className="text-gray-600 max-w-2xl mx-auto">
              Our SNMP Outlet Control System provides comprehensive management
              of your Raritan PDU devices with these powerful features.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {[
              {
                icon: <Power className="w-6 h-6" />,
                title: "Outlet Control",
                description:
                  "Toggle power outlets on/off remotely with secure SNMP commands",
              },
              {
                icon: <Activity className="w-6 h-6" />,
                title: "Real-time Monitoring",
                description: "Live status updates of all connected PDU outlets",
              },
              {
                icon: <LineChart className="w-6 h-6" />,
                title: "Historical Data",
                description:
                  "Track voltage and current trends with interactive visualizations",
              },
              {
                icon: <Shield className="w-6 h-6" />,
                title: "Secure Access",
                description:
                  "Role-based authentication with Supabase integration",
              },
            ].map((feature, index) => (
              <div
                key={index}
                className="p-6 bg-white rounded-xl shadow-sm hover:shadow-md transition-shadow"
              >
                <div className="text-blue-600 mb-4">{feature.icon}</div>
                <h3 className="text-xl font-semibold mb-2">{feature.title}</h3>
                <p className="text-gray-600">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Technical Details Section */}
      <section className="py-20 bg-gray-50">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold mb-4">Technical Architecture</h2>
            <p className="text-gray-600 max-w-2xl mx-auto">
              Built with modern technologies for reliability, security, and
              performance.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <div className="p-6 bg-white rounded-xl shadow-sm hover:shadow-md transition-shadow text-center">
              <div className="text-blue-600 mb-4 flex justify-center">
                <Server className="w-10 h-10" />
              </div>
              <h3 className="text-xl font-semibold mb-2">FastAPI Backend</h3>
              <p className="text-gray-600">
                Python-based agent that handles SNMP GET/SET operations to
                communicate with PDU devices
              </p>
            </div>

            <div className="p-6 bg-white rounded-xl shadow-sm hover:shadow-md transition-shadow text-center">
              <div className="text-blue-600 mb-4 flex justify-center">
                <Database className="w-10 h-10" />
              </div>
              <h3 className="text-xl font-semibold mb-2">
                Supabase Integration
              </h3>
              <p className="text-gray-600">
                Secure authentication and data storage for user management and
                historical readings
              </p>
            </div>

            <div className="p-6 bg-white rounded-xl shadow-sm hover:shadow-md transition-shadow text-center">
              <div className="text-blue-600 mb-4 flex justify-center">
                <Wifi className="w-10 h-10" />
              </div>
              <h3 className="text-xl font-semibold mb-2">SNMP Protocol</h3>
              <p className="text-gray-600">
                Industry-standard protocol for network device management and
                monitoring
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-blue-600 text-white">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl font-bold mb-4">
            Ready to Control Your PDU Infrastructure?
          </h2>
          <p className="text-white opacity-90 mb-8 max-w-2xl mx-auto">
            Access your secure dashboard to start monitoring and controlling
            your PDU outlets.
          </p>
          <a
            href="/dashboard"
            className="inline-flex items-center px-8 py-4 text-blue-600 bg-white rounded-lg hover:bg-gray-100 transition-colors font-medium"
          >
            Access Dashboard
            <ArrowUpRight className="ml-2 w-5 h-5" />
          </a>
        </div>
      </section>

      <Footer />
    </div>
  );
}
