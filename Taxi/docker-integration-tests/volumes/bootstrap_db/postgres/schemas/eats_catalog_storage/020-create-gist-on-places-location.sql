CREATE INDEX CONCURRENTLY idx__places__location 
     ON storage.places USING gist(location);
