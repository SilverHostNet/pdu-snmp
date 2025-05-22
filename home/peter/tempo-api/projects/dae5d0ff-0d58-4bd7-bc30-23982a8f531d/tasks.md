✅ SNMP Connector MVP — Task-Based Build Plan
🧱 PHASE 1: Project Initialization
1. Initialize Next.js frontend project
Start: No frontend project exists

End: Next.js app bootstrapped using App Router

Command: npx create-next-app@latest web-ui --app --typescript

2. Initialize Supabase project
Start: No Supabase project

End: Supabase project created, with anon and service keys available

3. Set up basic Supabase Auth in Next.js
Start: Just frontend shell

End: User can sign up/sign in via email (use Supabase client)

Test: Visiting /auth allows login/signup with working redirects

4. Add Tailwind CSS to Next.js
Start: Default styles

End: Tailwind configured, utility classes render correctly

5. Scaffold page routes
Start: App shell

End: Routes created: /auth, /dashboard, /outlet/[id]

Test: All pages show unique placeholder content

🖥️ PHASE 2: Local SNMP Agent Setup
6. Initialize Python SNMP agent (FastAPI)
Start: Empty agent/ directory

End: main.py runs FastAPI server on port 5000 with /healthz

Test: GET /healthz returns { status: "ok" }

7. Add SNMP GET function to agent
Start: FastAPI server only

End: GET /outlet-status/{outlet_id} performs SNMP GET using hardcoded OID

Test: Returns fake value if SNMP not reachable

8. Add SNMP SET function (turn outlet ON/OFF)
Start: Only SNMP GET available

End: POST /outlet-control/{outlet_id} accepts { action: "on" | "off" | "cycle" } and performs snmpset

Test: Returns 200/500 based on SNMP outcome

9. Add .env file to agent
Start: IP/strings hardcoded

End: Load SNMP community and PDU IP from .env using python-dotenv

Test: Break if missing

10. Test SNMP agent against live Raritan PX3
Start: SNMP running, but untested

End: Validate real snmpget/set with pysnmp or netsnmp

Test: Outlet state toggled via POST

📡 PHASE 3: Connect UI to Agent
11. Create API wrapper in Next.js for agent endpoints
Start: Agent running independently

End: Frontend uses fetch to call GET /outlet-status and POST /outlet-control

Test: Console logs response

12. Build UI for outlet list
Start: No UI for outlets

End: GET /outlet-status populates a card per outlet showing state

Test: Cards visually show ON or OFF

13. Add buttons to toggle outlet ON/OFF
Start: Static state

End: Buttons call POST to change outlet state

Test: Verify API hit and new state fetched

14. Add loading and error state UI
Start: No error handling

End: Show spinner while loading, error banner if API fails

Test: Simulate bad PDU IP

🧾 PHASE 4: Supabase Integration
15. Create outlet_readings table
Start: No schema

End: Run schema.sql or use Supabase UI to create outlet_readings table

Test: Insert test row manually

16. Push outlet readings from agent to Supabase
Start: Agent logs nowhere

End: After each successful SNMP GET/SET, agent logs state to outlet_readings

Test: Check DB for new rows

17. Fetch historical readings in dashboard
Start: UI shows live state only

End: /dashboard fetches and graphs voltage/current over time (e.g. last 24h)

Test: Graph shows mock Supabase data

🔐 PHASE 5: Production Prep
18. Protect all dashboard routes
Start: Routes open

End: Only logged-in users can see /dashboard

Test: Try access when not signed in

19. Add service account support to agent
Start: Agent has full DB access

End: Use Supabase service key from .env and restrict DB insertions

Test: Fail with bad token

20. Create a systemd service to auto-start the agent
Start: Agent runs manually

End: Add a .service file, enable/start it on boot

Test: Reboot and confirm it starts

🏁 Final MVP Outcome
Authenticated user logs in via Supabase

Sees a dashboard of all outlets with live status

Can toggle outlet state (on/off/cycle)

Agent fetches SNMP data and updates Supabase

Supabase holds outlet history for graphing

Agent runs as service on local Ubuntu 22.04

