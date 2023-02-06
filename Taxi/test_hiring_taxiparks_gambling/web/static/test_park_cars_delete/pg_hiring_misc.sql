INSERT INTO hiring_taxiparks_gambling_salesforce.cars (
    sf_id,
    model,
    brand,
    rental_cost_min,
    scheme_of_work,
    park_conditions_id,
    is_deleted
) VALUES
(
    'car 1',
    'Avensis',
    'Ferrari',
    1500,
    'Rent',
    'park 1',
    FALSE
),(
    'car 2',
    'Avensis',
    'Ferrari',
    1600,
    'Salary',
    'park 1',
    FALSE
),(
    'deleted car',
    'Avensis',
    'Ferrari',
    1700,
    'Salary',
    'park 1',
    TRUE
);
