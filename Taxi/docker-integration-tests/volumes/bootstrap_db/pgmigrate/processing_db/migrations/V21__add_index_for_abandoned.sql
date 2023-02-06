CREATE INDEX find_abandoned_index ON processing.events(scope, queue, due) WHERE need_handle;
