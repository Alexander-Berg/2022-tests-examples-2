CREATE INDEX find_abandoned_index_2 ON processing.events(scope, queue, due)
    WHERE need_handle AND NOT is_malformed;
