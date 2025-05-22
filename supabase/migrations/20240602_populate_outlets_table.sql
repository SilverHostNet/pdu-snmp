-- Populate outlets table with initial data
INSERT INTO outlets (outlet_number, name)
VALUES 
  (1, 'Server Rack PDU 1'),
  (2, 'Network Switch PDU'),
  (3, 'Storage Array PDU'),
  (4, 'Backup System PDU'),
  (5, 'Dev Environment PDU'),
  (6, 'Test Environment PDU'),
  (7, 'Monitoring System PDU'),
  (8, 'Security System PDU')
ON CONFLICT (outlet_number) DO UPDATE
  SET name = EXCLUDED.name;

-- Add initial readings for each outlet
INSERT INTO outlet_readings (outlet_id, state, voltage, current)
SELECT 
  id,
  CASE WHEN outlet_number % 2 = 0 THEN 'off' ELSE 'on' END,
  CASE WHEN outlet_number % 2 = 0 THEN 0 ELSE 120 END,
  CASE 
    WHEN outlet_number % 2 = 0 THEN 0 
    ELSE GREATEST(1, outlet_number % 6)
  END
FROM outlets
WHERE outlet_number BETWEEN 1 AND 8;

-- Add some historical readings for trending data
INSERT INTO outlet_readings (outlet_id, state, voltage, current, created_at)
SELECT 
  id,
  CASE WHEN outlet_number % 2 = 0 THEN 'off' ELSE 'on' END,
  CASE WHEN outlet_number % 2 = 0 THEN 0 ELSE 120 END,
  CASE 
    WHEN outlet_number % 2 = 0 THEN 0 
    ELSE GREATEST(1, outlet_number % 6) + (random() * 0.5)::int
  END,
  now() - (interval '1 hour' * generate_series(1, 24))
FROM outlets
WHERE outlet_number BETWEEN 1 AND 8;