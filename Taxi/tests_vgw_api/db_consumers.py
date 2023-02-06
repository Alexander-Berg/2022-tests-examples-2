import collections


SELECT_CONSUMER_GATEWAYS = """
SELECT * FROM consumers.consumer_voice_gateways
WHERE gateway_id = '{}'
"""


def select_consumers(pgsql):
    cursor = pgsql['vgw_api'].cursor()
    cursor.execute(
        'SELECT '
        'cc.id, cc.name, cc.enabled, cc.quota, '
        'array_remove(array_agg(ccvg.gateway_id), NULL)'
        'FROM consumers.consumers cc '
        'LEFT JOIN consumers.consumer_voice_gateways ccvg '
        'ON cc.id = ccvg.consumer_id '
        'GROUP BY cc.id',
    )
    result = cursor.fetchall()
    cursor.close()
    consumers = []
    consumer = collections.namedtuple(
        'Consumer', ['id', 'name', 'enabled', 'gateway_ids'],
    )
    for row in result:
        assert row[3] == 0  # quota is deprecated and must be 0
        consumers.append(consumer(row[0], row[1], row[2], row[4]))
    return consumers


def select_consumer_voice_gateways(pgsql):
    cursor = pgsql['vgw_api'].cursor()
    cursor.execute(
        'SELECT * FROM consumers.consumer_voice_gateways '
        'ORDER BY consumer_id ASC ',
    )
    result = cursor.fetchall()
    cursor.close()
    return result


def select_consumer_vg_by_gateway(pgsql, gateway_id):
    cursor = pgsql['vgw_api'].cursor()
    cursor.execute(SELECT_CONSUMER_GATEWAYS.format(gateway_id))
    result = cursor.fetchall()
    cursor.close()
    gateways = []
    konsumer_gateway = collections.namedtuple(
        'ConsumerGateway', ['consumer_id', 'gateway_id'],
    )
    for row in result:
        gateways.append(konsumer_gateway(row[0], row[1]))
    return result


def select_consumer_enabled(pgsql, consumer_id):
    cursor = pgsql['vgw_api'].cursor()
    cursor.execute(
        'SELECT enabled FROM consumers.consumers '
        'WHERE id = %s' % consumer_id,
    )
    result = cursor.fetchall()
    cursor.close()
    return result[0][0]
