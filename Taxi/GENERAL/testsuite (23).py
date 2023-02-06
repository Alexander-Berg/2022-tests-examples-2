from copy import deepcopy

from ._default import params as default_params


params = deepcopy(default_params)

MOCKSERVER_URL = 'http://@@MOCKSERVER@@'

fastcgi_params = params['fastcgi.conf']
fastcgi_params['taximeter_core_base_url'] = MOCKSERVER_URL + '/taximeter-core'
fastcgi_params['geotracks_base_url'] = MOCKSERVER_URL + '/geotracks'
fastcgi_params['driver_protocol_base_url'] = (
    MOCKSERVER_URL + '/driver-protocol'
)
fastcgi_params['dispatch_buffer_base_url'] = (
    MOCKSERVER_URL + '/dispatch-buffer'
)
fastcgi_params['archive_base_url'] = MOCKSERVER_URL + '/archive-api'
fastcgi_params['order_archive_base_url'] = MOCKSERVER_URL + '/order-archive'
fastcgi_params['stq_agent_base_url'] = MOCKSERVER_URL + '/stq-agent'
fastcgi_params['cars_catalog_base_url'] = MOCKSERVER_URL + '/cars-catalog'
fastcgi_params['territories_base_url'] = MOCKSERVER_URL + '/territories'
fastcgi_params['user_api_base_url'] = MOCKSERVER_URL + '/user-api'
fastcgi_params['selfemployed_base_url'] = MOCKSERVER_URL + '/selfemployed'
fastcgi_params['mlaas_base_url'] = MOCKSERVER_URL + '/mlaas'
fastcgi_params['umlaas_base_url'] = MOCKSERVER_URL + '/umlaas'
fastcgi_params['tags_base_url'] = MOCKSERVER_URL + '/tags'
fastcgi_params['passenger_tags_base_url'] = MOCKSERVER_URL + '/passenger-tags'
fastcgi_params['async_pool_size'] = 32
fastcgi_params['mds_upload_host'] = MOCKSERVER_URL
fastcgi_params['mds_get_host'] = MOCKSERVER_URL
fastcgi_params['experiments_base_url'] = MOCKSERVER_URL + '/experiments'
fastcgi_params['persuggest_base_url'] = MOCKSERVER_URL + '/persuggest'
fastcgi_params['pickuppoints_base_url'] = MOCKSERVER_URL + '/special-zones'
fastcgi_params['parks_base_url'] = MOCKSERVER_URL + '/parks'
fastcgi_params['vgw_api_url'] = MOCKSERVER_URL + '/vgw-api'
fastcgi_params['order_core_base_url'] = MOCKSERVER_URL + '/order-core'
fastcgi_params['order_offers_base_url'] = MOCKSERVER_URL + '/order-offers'

fastcgi_params['work_pool_threads'] = 10
fastcgi_params['external_work_pool_threads'] = 10
fastcgi_params['geo_pool_threads'] = 10
fastcgi_params['routestats_pool_threads'] = 10

params['fastcgi.conf']['pool_logger_path'] = ''
params['fastcgi.conf']['ml_logger_path'] = ''

params['fastcgi.conf'].update(
    {
        'router_here_url': MOCKSERVER_URL + '/router_here',
        'router_here_matrix_url': MOCKSERVER_URL + '/router_here',
        'afs_base_url': MOCKSERVER_URL + '/antifraud',
        'uafs_base_url': MOCKSERVER_URL + '/uantifraud',
    },
)
params['fastcgi.conf']['driver_ratings_codegen_base_url'] = (
    MOCKSERVER_URL + '/driver-ratings'
)

fastcgi_params['driver_profiles_base_url'] = (
    MOCKSERVER_URL + '/driver-profiles'
)
