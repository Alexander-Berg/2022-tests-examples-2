
/* V1 */
INSERT INTO scripts.js_scripts
(id, bonus_name, revision, updated, type, content)
VALUES
(
    1,
    'bonus-for-airport-route',
    0,
    '2019-02-03T00:00:00+00',
    'calculate',
    '
    let source = order_context.route_point_info[0];
    var diff = 0;
    if (source.is_airport) {
      diff += 1;
    }
    if (source.geoareas.includes("lipetsk_airport")) {
      diff += 2;
    }

    if (order_context.route_point_info.length > 1) {
      diff += 3;
      let any_point = order_context.route_point_info[1];
      if (any_point.is_airport) {
        diff += 4;
      }
    }
    return diff;
    '
);

INSERT INTO scripts.active_scripts
(id, updated, bonus_name, type, script_id)
VALUES
(
    2,
    '2019-02-03T00:00:00+00',
    'bonus-for-airport-route',
    'calculate',
    1
);
