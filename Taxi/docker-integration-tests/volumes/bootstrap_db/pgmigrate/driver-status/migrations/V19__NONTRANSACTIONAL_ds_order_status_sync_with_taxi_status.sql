ALTER TYPE ds.order_status RENAME VALUE 'calling' TO 'calling_obsolete';
ALTER TYPE ds.order_status ADD VALUE 'preexpired';
ALTER TYPE ds.order_status ADD VALUE 'unknown';
