ALTER TABLE balancers.entry_points ADD COLUMN domain_id TEXT;

/*
 TODO
 than domain_id became required
 create uniq index for domain_id + awacs_upstream_id
 thus dns_name == domain_id its not strongly needed for now
*/
