-- Create tables for outlet management

-- Outlets table to store PDU outlet configurations
CREATE TABLE IF NOT EXISTS outlets (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  pdu_id TEXT NOT NULL,
  outlet_number INTEGER NOT NULL,
  name TEXT NOT NULL,
  description TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  UNIQUE(pdu_id, outlet_number)
);

-- Outlet readings table to store historical measurements
CREATE TABLE IF NOT EXISTS outlet_readings (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  outlet_id UUID REFERENCES outlets(id),
  state TEXT NOT NULL,
  voltage NUMERIC,
  current NUMERIC,
  power NUMERIC,
  energy NUMERIC,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Outlet events table to store state changes and actions
CREATE TABLE IF NOT EXISTS outlet_events (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  outlet_id UUID REFERENCES outlets(id),
  event_type TEXT NOT NULL,
  description TEXT,
  user_id UUID,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Tables are already added to supabase_realtime publication
-- No need to add them again
