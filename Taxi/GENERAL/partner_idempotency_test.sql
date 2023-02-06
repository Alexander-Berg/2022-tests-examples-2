/**
This query returns partner_id if already have suitable partner.
Args:
$1 - chain_id (can be null)
$2 - array of business_oids
 */

SELECT partner_id
FROM location
WHERE business_oid = ANY ($2::BIGINT[])
UNION
SELECT id as partner_id
FROM partner
WHERE partner.geo_chain_id = $1::BIGINT
;
