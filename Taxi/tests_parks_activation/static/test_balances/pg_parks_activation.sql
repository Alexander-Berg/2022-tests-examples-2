INSERT INTO parks_activation.accounts (park_id, city_id, promised_payment_till,
                                       threshold, dynamic_threshold, recommended_payments,
                                       mongo_revision, require_card, require_coupon, has_corp_vat) VALUES
('100', 'spb', '1970-01-15T06:56:07.000'::TIMESTAMPTZ, 10.1, 35.0,
 '{}'::parks_activation.recommended_payment_t[],'rev1', false, true,  true),
('200', 'moscow', null, null, null,
 ARRAY[( 123, 10.5 )::parks_activation.recommended_payment_t, ( 124, 11.5 )::parks_activation.recommended_payment_t],
 'rev1', true, false, true),
('300', 'moscow', null, null, null,
 ARRAY[( 123, 10.5 )::parks_activation.recommended_payment_t, ( 124, 11.5 )::parks_activation.recommended_payment_t],
 'rev2', true, false, true);

INSERT INTO parks_activation.parks (park_id, deactivated, deactivated_reason,
                                    can_cash, can_card, can_coupon, can_corp, can_subsidy, updated, revision) VALUES
('100', false, null, false, false, true, false, false, '1970-01-15T06:56:07.000'::TIMESTAMPTZ, 1),
('200', true, 'reason1', true, true, false, true, false,  '1970-01-15T06:56:07.000'::TIMESTAMPTZ, 2),
('300', true, 'reason2', true, true, false, true, false, '1970-01-15T06:56:07.000'::TIMESTAMPTZ, 3);
