CREATE TABLE IF NOT EXISTS combo_contractors.contractor_0
  PARTITION OF combo_contractors.contractor
  FOR VALUES IN (0);

CREATE TABLE IF NOT EXISTS combo_contractors.contractor_1
  PARTITION OF combo_contractors.contractor
  FOR VALUES IN (1);

CREATE TABLE IF NOT EXISTS combo_contractors.contractor_2
  PARTITION OF combo_contractors.contractor
  FOR VALUES IN (2);

CREATE TABLE IF NOT EXISTS combo_contractors.contractor_3
  PARTITION OF combo_contractors.contractor
  FOR VALUES IN (3);
