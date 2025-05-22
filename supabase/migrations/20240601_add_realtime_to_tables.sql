-- Enable realtime for the outlet tables

-- Add tables to the supabase_realtime publication if they don't exist already
DO $$
BEGIN
  -- Check if outlets table is already in the publication
  IF NOT EXISTS (
    SELECT 1 FROM pg_publication_tables 
    WHERE pubname = 'supabase_realtime' AND tablename = 'outlets'
  ) THEN
    alter publication supabase_realtime add table outlets;
  END IF;

  -- Check if outlet_readings table is already in the publication
  IF NOT EXISTS (
    SELECT 1 FROM pg_publication_tables 
    WHERE pubname = 'supabase_realtime' AND tablename = 'outlet_readings'
  ) THEN
    alter publication supabase_realtime add table outlet_readings;
  END IF;

  -- Check if outlet_events table is already in the publication
  IF NOT EXISTS (
    SELECT 1 FROM pg_publication_tables 
    WHERE pubname = 'supabase_realtime' AND tablename = 'outlet_events'
  ) THEN
    alter publication supabase_realtime add table outlet_events;
  END IF;
END
$$;