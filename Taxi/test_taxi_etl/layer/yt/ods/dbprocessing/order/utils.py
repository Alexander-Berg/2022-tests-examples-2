

def create_order_proc(type_=None, status_updates=None, calc_method=None,
                      status=None, taxi_status=None, created=None,
                      status_updated=None, driver_uuid=None, clid=None):
    return dict(
        order=dict(_type=type_,
                   calc_method=calc_method,
                   status=status,
                   taxi_status=taxi_status,
                   created=created,
                   status_updated=status_updated,
                   performer=dict(uuid=driver_uuid, clid=clid)),
        order_info=dict(statistics=dict(status_updates=status_updates))
    )


def create_data_for_cost_before_antisurge(**kwargs):
    return {
        'order': {
            'created': kwargs.get('created'),
            'calc': kwargs.get('calc'),
            'request': {
                'class': kwargs.get('request_class')
            },
            'performer': {
                'tariff': {
                    'class': kwargs.get('driver_tariff')
                }
            },
            'source': kwargs.get('source')
        }
    }


def create_by_paths(dict_values: dict) -> dict:
    doc = dict()
    for path, value in dict_values.items():
        node = doc
        parts = path.split('.')
        for part in parts[:-1]:
            if part not in node:
                node[part] = dict()
            node = node[part]
        node[parts[-1]] = value
    return doc
