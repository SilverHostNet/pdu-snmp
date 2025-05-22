-- Create tables for agent and device management

-- Agents table to store SNMP agent connection details
CREATE TABLE IF NOT EXISTS agents (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name TEXT NOT NULL,
  host TEXT NOT NULL,
  port INTEGER NOT NULL DEFAULT 5000,
  status TEXT NOT NULL DEFAULT 'unknown',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  user_id UUID REFERENCES auth.users(id)
);

-- Devices table to store PDU device details
CREATE TABLE IF NOT EXISTS devices (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name TEXT NOT NULL,
  host TEXT NOT NULL,
  snmp_community TEXT NOT NULL DEFAULT 'public',
  snmp_version TEXT NOT NULL DEFAULT '2c',
  model TEXT,
  num_outlets INTEGER DEFAULT 8,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  agent_id UUID NOT NULL REFERENCES agents(id) ON DELETE CASCADE
);

-- Outlet readings table to store historical data
CREATE TABLE IF NOT EXISTS outlet_readings (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  outlet_id TEXT NOT NULL,
  state TEXT,
  voltage NUMERIC,
  current NUMERIC,
  power NUMERIC,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Outlet events table to store state changes
CREATE TABLE IF NOT EXISTS outlet_events (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  outlet_id TEXT NOT NULL,
  event_type TEXT NOT NULL,
  new_state TEXT,
  user_initiated BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Add RLS policies
ALTER TABLE agents ENABLE ROW LEVEL SECURITY;
ALTER TABLE devices ENABLE ROW LEVEL SECURITY;
ALTER TABLE outlet_readings ENABLE ROW LEVEL SECURITY;
ALTER TABLE outlet_events ENABLE ROW LEVEL SECURITY;

-- Allow authenticated users to view their own agents
DROP POLICY IF EXISTS "Users can view their own agents";
CREATE POLICY "Users can view their own agents"
  ON agents FOR SELECT
  USING (auth.uid() = user_id);

-- Allow authenticated users to insert their own agents
DROP POLICY IF EXISTS "Users can insert their own agents";
CREATE POLICY "Users can insert their own agents"
  ON agents FOR INSERT
  WITH CHECK (auth.uid() = user_id);

-- Allow authenticated users to update their own agents
DROP POLICY IF EXISTS "Users can update their own agents";
CREATE POLICY "Users can update their own agents"
  ON agents FOR UPDATE
  USING (auth.uid() = user_id);

-- Allow authenticated users to view devices linked to their agents
DROP POLICY IF EXISTS "Users can view devices linked to their agents";
CREATE POLICY "Users can view devices linked to their agents"
  ON devices FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM agents
      WHERE agents.id = devices.agent_id
      AND agents.user_id = auth.uid()
    )
  );

-- Allow authenticated users to insert devices linked to their agents
DROP POLICY IF EXISTS "Users can insert devices linked to their agents";
CREATE POLICY "Users can insert devices linked to their agents"
  ON devices FOR INSERT
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM agents
      WHERE agents.id = devices.agent_id
      AND agents.user_id = auth.uid()
    )
  );

-- Allow authenticated users to update devices linked to their agents
DROP POLICY IF EXISTS "Users can update devices linked to their agents";
CREATE POLICY "Users can update devices linked to their agents"
  ON devices FOR UPDATE
  USING (
    EXISTS (
      SELECT 1 FROM agents
      WHERE agents.id = devices.agent_id
      AND agents.user_id = auth.uid()
    )
  );

-- For now, allow all authenticated users to read outlet readings and events
DROP POLICY IF EXISTS "Allow authenticated users to read outlet readings";
CREATE POLICY "Allow authenticated users to read outlet readings"
  ON outlet_readings FOR SELECT
  USING (auth.role() = 'authenticated');

DROP POLICY IF EXISTS "Allow authenticated users to read outlet events" ON outlet_events;
CREATE POLICY "Allow authenticated users to read outlet events"
  ON outlet_events FOR SELECT
  USING (auth.role() = 'authenticated');

-- Add to realtime publication
alter publication supabase_realtime add table agents;
alter publication supabase_realtime add table devices;
alter publication supabase_realtime add table outlet_readings;
alter publication supabase_realtime add table outlet_events;
