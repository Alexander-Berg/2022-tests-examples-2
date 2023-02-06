INSERT INTO relocator.rules(rule_id, offer_interval, mode_id, description, icon, name, subname, tags, completed_tags, accept_ttl, complete_ttl, send_offer, display_name, min_time_since_completed_offer)
VALUES (1001, ('60 second')::interval, 1488, 'SuperSurge description', 'star', 'SuperSurge name', 'SuperSurge subname', array['tag1'], array['completed_tag1'], ('5 minutes')::interval, ('60 second')::interval, true, 'some-rule', ('600 seconds')::interval);


INSERT INTO relocator.filters(rule_id, source_geoareas_in)
  VALUES (1001, array['moscow', 'tula']);

INSERT INTO relocator.filters(rule_id, source_geoareas_not_in)
  VALUES (1001, array['svo']);

INSERT INTO relocator.filters(rule_id, source_surge_range)
  VALUES (1001, (0, 0.8)::relocator.double_range);

INSERT INTO relocator.filters(rule_id, air_distance_range)
VALUES (1001, (100, 10000)::relocator.double_range);

INSERT INTO relocator.filters(rule_id, statuses_in)
  VALUES (1001, array['free']);

INSERT INTO relocator.filters(rule_id, classes_in)
  VALUES (1001, array['comfort', 'business']);

INSERT INTO relocator.filters(rule_id, classes_not_in)
  VALUES (1001, array['econom']);

INSERT INTO relocator.filters(rule_id, dest_surge_range)
  VALUES (1001, (2, 100)::relocator.double_range);

INSERT INTO relocator.filters(rule_id, surge_gradient_range)
  VALUES (1001, (1, 100)::relocator.double_range);

INSERT INTO relocator.filters(rule_id, router_time_range)
  VALUES (1001, (300, 1200)::relocator.double_range);

INSERT INTO relocator.filters(rule_id, score_range)
  VALUES (1001, ((0.1, -0.5, 2.0)::relocator.score_coeffs, (-0.3, 0.5, 960)::relocator.score_coeffs, (0, 1000)::relocator.double_range)::relocator.score_range);

INSERT INTO relocator.filters(rule_id, score_top)
VALUES (1001, ((0.1, -0.5, 2.0)::relocator.score_coeffs, (-0.3, 0.5, 960)::relocator.score_coeffs, (5, true, 'Driver')::relocator.top)::relocator.score_top);

INSERT INTO relocator.filters(rule_id, router_time_top)
VALUES (1001, (1, false, 'Driver')::relocator.top);

INSERT INTO relocator.filters(rule_id, pins_gradient_percentage_range)
  VALUES (1001, (0, 0.8)::relocator.double_range);

INSERT INTO relocator.filters(rule_id, pins_gradient_value_range)
  VALUES (1001, (1, 100)::relocator.double_range);

INSERT INTO relocator.filters(rule_id, price_gradient_percentage_range)
  VALUES (1001, (0, 0.8)::relocator.double_range);

INSERT INTO relocator.filters(rule_id, price_gradient_value_range)
  VALUES (1001, (1, 100)::relocator.double_range);

INSERT INTO relocator.filters(rule_id, dest_area_sent_offers_range)
  VALUES (1001, (0, 3000)::relocator.double_range);

INSERT INTO relocator.filters(rule_id, dest_area_accepted_offers_range)
  VALUES (1001, (0, 700)::relocator.double_range);

INSERT INTO relocator.filters(rule_id, dest_geoareas_in)
  VALUES (1001, array['moscow', 'tula']);

INSERT INTO relocator.filters(rule_id, dest_geoareas_not_in)
  VALUES (1001, array['svo']);

INSERT INTO relocator.filters(rule_id, pscore_range)
  VALUES (1001, ((0.1, -0.5, 2.0)::relocator.score_coeffs, (-0.3, 0.5, 960)::relocator.score_coeffs,
  (1.0, 2.0, 3.0, 4.0, 6.0, 5.0)::relocator.pscore_coeffs, (1.1, 1.2, 1.3, 1.4, 1.6, 1.5)::relocator.pscore_coeffs,
  (0, 1000)::relocator.double_range)::relocator.pscore_range);

INSERT INTO relocator.filters(rule_id, pscore_top)
  VALUES (1001, ((0.1, -0.5, 2.0)::relocator.score_coeffs, (-0.3, 0.5, 960)::relocator.score_coeffs,
  (1.0, 2.0, 3.0, 4.0, 6.0, 5.0)::relocator.pscore_coeffs, (1.1, 1.2, 1.3, 1.4, 1.6, 1.5)::relocator.pscore_coeffs,
  (5, true, 'Driver')::relocator.top)::relocator.pscore_top);
