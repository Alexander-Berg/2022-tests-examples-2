-- kTestSubscriptionIdempotencyToken
-- ARGS:
--  $1::TEXT        idempotency

SELECT EXISTS(
    SELECT 1
    FROM
        logistic_supply_conductor.subscription_idempotency_tokens
    WHERE
        idempotency = $1::TEXT
);
