START TRANSACTION;

ALTER TABLE clownductor.services ADD COLUMN design_review_ticket TEXT;

COMMIT;
