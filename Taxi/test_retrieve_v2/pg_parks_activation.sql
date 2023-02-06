INSERT INTO parks_activation.accounts (park_id, city_id, promised_payment_till,
                                       threshold, dynamic_threshold, recommended_payments,
                                       mongo_revision, require_card, require_coupon, has_corp_vat) VALUES
('park1', 'spb', '1970-01-15T06:56:07.000'::TIMESTAMPTZ, 0.1,  0.1,
 '{}'::parks_activation.recommended_payment_t[], 'rev1', false, true, true),
('park2', 'moscow', null, null, null,
 ARRAY[( 123, 10.5 )::parks_activation.recommended_payment_t, ( 124, 11.5 )::parks_activation.recommended_payment_t],
 'rev1', true, false, true),
('park3', 'moscow', null, null, null,
 ARRAY[( 123, 10.5 )::parks_activation.recommended_payment_t, ( 124, 11.5 )::parks_activation.recommended_payment_t],
 'rev2', true, false, true);

INSERT INTO parks_activation.parks (park_id, deactivated, deactivated_reason,
                                    can_cash, can_card, can_coupon, can_corp, has_corp_without_vat_contract, can_corp_without_vat, can_subsidy,
                                    can_logistic, logistic_deactivated, logistic_deactivated_reason, logistic_can_cash,
                                    logistic_can_card, logistic_can_subsidy, updated, revision) VALUES
('park1', false, null, false, false, true, false, false, false, false, true, false, null, true, true, false,
 '1970-01-15T06:56:07.000'::TIMESTAMPTZ, 1),
('park2', true, 'reason1', true, true, false, true, false, false, false, true, true, 'logistic reason1', false, false, false,
 '1970-01-15T06:56:07.000'::TIMESTAMPTZ, 2),
('park3', false, null, true, false, true, false, true, true, false, true, true, 'logistic reason2', false, true, false,
 '1970-01-15T06:56:07.000'::TIMESTAMPTZ, 3);
