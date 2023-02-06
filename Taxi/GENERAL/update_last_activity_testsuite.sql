UPDATE eats_partners.last_activity
SET last_activity_at = $1
WHERE partner_id = $2
