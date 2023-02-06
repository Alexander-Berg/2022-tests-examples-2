CREATE TABLE feedbacks_0
  ( 
     park_id          VARCHAR(32) NOT NULL, --0
     id               VARCHAR(32) NOT NULL, --1
     date             TIMESTAMP NOT NULL,   --2
     date_last_change TIMESTAMP,            --3
     feed_type        INTEGER NOT NULL,     --4
     status           INTEGER NOT NULL,     --5
     description      VARCHAR(1024),        --6
     score            INTEGER,              --7
     driver_id        VARCHAR(32),          --8
     driver_name      VARCHAR(128),         --9
     driver_signal    VARCHAR(32),          --10
     order_id         VARCHAR(32),          --11
     order_number     INTEGER,              --12
     user_name        VARCHAR(64),          --13
     predefined_comments VARCHAR(256),      --14
     CONSTRAINT feedbacks_pkey PRIMARY KEY (park_id, id) 
  ); 

CREATE INDEX idx_feedbacks_date_last_change 
  ON feedbacks_0 (date_last_change); 

CREATE INDEX idx_feedbacks_park_id_order_id 
  ON feedbacks_0 (park_id, order_id);
