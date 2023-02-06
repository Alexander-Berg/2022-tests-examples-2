import datetime


def get_all_orders(db, optional_fields=()):
    cursor = db.cursor()
    selector = (
        'SELECT order_id, updated_ts, created_ts, check_in_ts, '
        'terminal_id, pickup_line, tariff_zone, user_id, user_locale, classes'
    )
    if optional_fields:
        selector += ', ' + ','.join(optional_fields)
    cursor.execute(selector + ' FROM dispatch_check_in.check_in_orders;')
    result = {}

    for raw in cursor:
        order_id = raw[0]
        updated_ts = raw[1]
        created_ts = raw[2]
        check_in_ts = raw[3]
        terminal_id = raw[4]
        pickup_line = raw[5]
        tariff_zone = raw[6]
        user_id = raw[7]
        user_locale = raw[8]
        classes = raw[9]

        key = order_id
        result[key] = {
            'updated_ts': updated_ts.astimezone(datetime.timezone.utc),
            'created_ts': created_ts.astimezone(datetime.timezone.utc),
            'check_in_ts': (
                None
                if check_in_ts is None
                else check_in_ts.astimezone(datetime.timezone.utc)
            ),
            'terminal_id': terminal_id,
            'pickup_line': pickup_line,
            'tariff_zone': tariff_zone,
            'user_id': user_id,
            'user_locale': user_locale,
            'classes': classes,
        }

        for idx, field in enumerate(optional_fields):
            result[key][field] = raw[idx + 10]
    return result


async def check_metric(monitor, metric_name, etalon_metric, labels):
    metrics = await monitor.get_metric('dispatch_check_in_metrics')
    if etalon_metric is None:
        assert metric_name not in metrics
    else:
        metric = metrics[metric_name]
        for label in labels:
            metric = metric[label]
        assert metric == etalon_metric


async def check_no_metrics(monitor):
    metric = await monitor.get_metric('dispatch_check_in_metrics')
    assert metric == {}
