🔌 Raritan PX3 SNMP Connector: System Architecture
🏗️ Overview
This architecture enables monitoring and control of a Raritan PX3 PDU via SNMP with:

Web UI (Next.js)

Backend agent on Ubuntu (Python + SNMP client)

Supabase (Auth, DB, REST API)

SNMP read/write (control + metrics)

📁 File + Folder Structure
1. web-ui/ — Next.js Frontend
ruby
Copy
Edit
web-ui/
├── app/                   # App Router Pages
│   ├── dashboard/         # Main dashboard
│   ├── auth/              # Auth pages (login/register)
│   └── api/               # Optional API routes
├── components/            # Shared React components (charts, cards, tables)
├── lib/                   # Supabase client, utils
├── styles/                # Tailwind or custom CSS
├── public/                # Static assets
├── .env.local             # Supabase client keys
└── next.config.js
2. agent/ — Local SNMP Agent on Ubuntu
bash
Copy
Edit
agent/
├── main.py                # Entry point: Flask/FastAPI app
├── snmp_client.py         # SNMP read/write logic using pysnmp or netsnmp
├── service_runner.py      # Optional: Systemd boot daemon
├── config.py              # Config loader for SNMP IPs and communities
├── requirements.txt
└── .env                   # SNMP secrets, Supabase service key
3. supabase/ — Supabase Project Setup
pgsql
Copy
Edit
supabase/
├── schema.sql             # DB schema for outlets, logs, users, etc.
├── functions/             # Edge Functions if needed
└── policies/              # RLS (Row Level Security) rules
🔌 How Each Part Works
✅ Frontend (Next.js)
Auth: Supabase Auth (email, magic links, or social)

Dashboard: Shows outlets, states (ON/OFF), voltages, current

Control UI: Buttons to toggle outlets

Fetches data from Supabase DB and/or local agent API

Realtime updates via Supabase realtime or polling

⚙️ Onsite Agent (Ubuntu)
Handles all SNMP logic:

snmpget for read (status, voltages, etc.)

snmpset for control (on/off/cycle outlet)

Serves a REST API (e.g., /outlets, /outlets/:id/on)

Pushes data to Supabase (via service role key)

Optionally handles trap logging using snmptrapd

🗃️ Supabase
Stores:

PDU outlet state history

Voltage/current snapshots

Users + auth

Offers RLS-secured APIs for frontend access

Realtime subscriptions to update frontend

Optional Edge Functions to proxy commands

🧠 State Management
State Type	Lives In	Accessed By
Auth session	Supabase Auth	Web UI (useSession)
Live outlet data	Supabase Realtime or agent API	Web UI
SNMP community/IP config	Agent .env or config.py	Agent only
Event logs, trap data	Supabase (pushed from agent)	Web UI dashboards

🔗 Services + Communication
plaintext
Copy
Edit
[ USER ] ⇆ [ Web UI (Next.js) ] ⇆ Supabase (Auth + DB)
                           ⇣
                    REST API Call
                           ⇣
                [ Local Agent (Ubuntu) ]
                           ⇅
                      SNMP (UDP)
                           ⇅
                 [ Raritan PX3 PDU ]
🔒 Security Considerations
SNMP v2c: Protect via VLAN isolation + firewalled agent

Supabase RLS: Lock data to authenticated users

HTTPS only for frontend/backend traffic

Supabase service key never exposed to clients (used only on agent)

📈 Supabase Table Ideas
sql
Copy
Edit
-- Outlet state snapshots
create table outlet_readings (
  id uuid primary key default uuid_generate_v4(),
  pdu_id text,
  outlet_number int,
  state text, -- on/off
  voltage int,
  current int,
  created_at timestamp default now()
);

-- Trap logs
create table trap_events (
  id uuid primary key default uuid_generate_v4(),
  message text,
  pdu_ip inet,
  event_type text,
  created_at timestamp default now()
);
📚 SNMP Reference (based on Raritan MIB)
Common OIDs from PDF:

Status: .1.3.6.1.4.1.13742.6.4.1.2.1.3.<pdu>.<outlet>

Power cycle: .1.3.6.1.4.1.13742.6.4.1.2.1.2.<pdu>.<outlet>

Inlet voltage: .1.3.6.1.4.1.13742.6.5.2.3.1.4.<pdu>.<inlet>.<sensor>

Trap handler config: /etc/snmp/snmptrapd.conf

✅ Suggested Tech Stack
Component	Tech
Frontend	Next.js (App Router + Tailwind)
Auth	Supabase Auth (email login)
Backend Agent	Python (Flask or FastAPI)
SNMP Client	pysnmp or netsnmp
DB + API	Supabase
Realtime	Supabase Realtime or polling
Local Daemon	Systemd unit (for auto start)