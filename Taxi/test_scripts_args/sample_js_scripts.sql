
/* V1 */
INSERT INTO scripts.js_scripts
(id, bonus_name, revision, updated, type, content)
VALUES
(
    0,
    'bonus-1',
    0,
    '2019-02-03T00:00:00+00',
    'calculate',
    '
        function assert_in(field, obj, obj_name) {
            if (!(field in obj))
                throw field + " not in " + obj_name + ": " + JSON.stringify(obj);
        }

        trace.text = "some text";

        assert_in("text", trace, "trace");
        assert_in("classes_priority_order", common_context, "common_context");
        assert_in("penalty_for_approximate_position", common_context, "common_context");
        assert_in("bonus_for_class_max_surge", common_context, "common_context");

        assert_in("search_from_request", order_context, "order_context");
        assert_in("dispatch_settings", order_context, "order_context");
        assert_in("pin_surge_by_classes", order_context, "order_context");

        assert_in("candidate_from_request", candidate_context, "candidate_context");
        assert_in("dbid", candidate_context, "candidate_context");
        assert_in("uuid", candidate_context, "candidate_context");
        assert_in("allowed_classes", candidate_context, "candidate_context");
        assert_in("driver_surge_by_classes", candidate_context, "candidate_context");
        assert_in("tags", candidate_context, "candidate_context");
        assert_in("reposition_check_result", candidate_context, "candidate_context");
        assert_in("tag_score_coeff", candidate_context, "candidate_context");
        assert_in("time_dist_weights", candidate_context, "candidate_context");
        return 100;
    '
);

INSERT INTO scripts.active_scripts
(id, updated, bonus_name, type, script_id)
VALUES
(
    0,
    '2019-02-03T00:00:00+00',
    'bonus-1',
    'calculate',
    0
);
