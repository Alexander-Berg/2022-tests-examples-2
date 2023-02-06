# flake8: noqa E501
import pytest


@pytest.mark.now('2019-10-30T20:10:00Z')
@pytest.mark.parametrize(
    'filters, params_ext, status, url',
    [
        (
            [],
            {},
            200,
            """https://kibana.taxi.yandex-team.ru/app/kibana#/discover?_g=('filters':!(('$state':('store':'appState'),'meta':('alias':'type','disabled':!f,'key':'query','negate':!f),'query':('query_string':('query':'type:"response"')))),'refreshInterval':('display':'Off','pause':!f,'value':0),'time':('from':'now-15m','mode':'quick','to':'now'))&_a=('columns':!('_source'),'index':'0','interval':'auto','sort':!('@timestamp','desc'))""",
        ),
        (
            [
                {'name': 'useragent', 'value': 'some'},
                {'name': 'http_code', 'value': '123'},
            ],
            {},
            400,
            '',
        ),
        (
            [{'name': 'http_code', 'value': '123'}],
            {},
            200,
            """https://kibana.taxi.yandex-team.ru/app/kibana#/discover?_g=('filters':!(('$state':('store':'appState'),'meta':('alias':'type','disabled':!f,'key':'query','negate':!f),'query':('query_string':('query':'type:"response"'))),('$state':('store':'appState'),'meta':('alias':'meta_code','disabled':!f,'key':'query','negate':!f),'query':('query_string':('query':'meta_code:123')))),'refreshInterval':('display':'Off','pause':!f,'value':0),'time':('from':'now-15m','mode':'quick','to':'now'))&_a=('columns':!('_source'),'index':'0','interval':'auto','sort':!('@timestamp','desc'))""",
        ),
        (
            [{'name': 'useragent', 'value': 'some'}],
            {},
            200,
            r"""https://kibana.taxi.yandex-team.ru/app/kibana#/discover?_g=('filters':!(('$state':('store':'appState'),'meta':('alias':'type','disabled':!f,'key':'query','negate':!f),'query':('query_string':('query':'type:"request"'))),('$state':('store':'appState'),'meta':('alias':'useragent','disabled':!f,'key':'query','negate':!f),'query':('query_string':('query':'useragent:*some*')))),'refreshInterval':('display':'Off','pause':!f,'value':0),'time':('from':'now-15m','mode':'quick','to':'now'))&_a=('columns':!('_source'),'index':'0','interval':'auto','sort':!('@timestamp','desc'))""",
        ),
        (
            [{'name': 'type', 'value': 'routestats'}],
            {},
            200,
            """https://kibana.taxi.yandex-team.ru/app/kibana#/discover?_g=('filters':!(('$state':('store':'appState'),'meta':('alias':'type','disabled':!f,'key':'query','negate':!f),'query':('query_string':('query':'type:"response" OR type:"periodic_task_finish"'))),('$state':('store':'appState'),'meta':('alias':'meta_type','disabled':!f,'key':'query','negate':!f),'query':('query_string':('query':'meta_type:routestats')))),'refreshInterval':('display':'Off','pause':!f,'value':0),'time':('from':'now-15m','mode':'quick','to':'now'))&_a=('columns':!('_source'),'index':'0','interval':'auto','sort':!('@timestamp','desc'))""",
        ),
        (
            [
                {'name': 'type', 'value': 'routestats,launch'},
                {'name': 'driver_id', 'value': '123abc'},
            ],
            {},
            200,
            """https://kibana.taxi.yandex-team.ru/app/kibana#/discover?_g=('filters':!(('$state':('store':'appState'),'meta':('alias':'type','disabled':!f,'key':'query','negate':!f),'query':('query_string':('query':'type:"response" OR type:"periodic_task_finish"'))),('$state':('store':'appState'),'meta':('alias':'meta_type','disabled':!f,'key':'query','negate':!f),'query':('query_string':('query':'meta_type:routestats OR meta_type:launch'))),('$state':('store':'appState'),'meta':('alias':'meta_driver_id','disabled':!f,'key':'query','negate':!f),'query':('query_string':('query':'meta_driver_id:"123abc"')))),'refreshInterval':('display':'Off','pause':!f,'value':0),'time':('from':'now-15m','mode':'quick','to':'now'))&_a=('columns':!('_source'),'index':'0','interval':'auto','sort':!('@timestamp','desc'))""",
        ),
        (
            [
                {'name': 'type', 'value': 'routestats*,l*h'},
                {'name': 'driver_id', 'value': '123abc'},
            ],
            {},
            200,
            r"""https://kibana.taxi.yandex-team.ru/app/kibana#/discover?_g=('filters':!(('$state':('store':'appState'),'meta':('alias':'type','disabled':!f,'key':'query','negate':!f),'query':('query_string':('query':'type:"response" OR type:"periodic_task_finish"'))),('$state':('store':'appState'),'meta':('alias':'meta_type','disabled':!f,'key':'query','negate':!f),'query':('query_string':('query':'meta_type:routestats* OR meta_type:l*h'))),('$state':('store':'appState'),'meta':('alias':'meta_driver_id','disabled':!f,'key':'query','negate':!f),'query':('query_string':('query':'meta_driver_id:"123abc"')))),'refreshInterval':('display':'Off','pause':!f,'value':0),'time':('from':'now-15m','mode':'quick','to':'now'))&_a=('columns':!('_source'),'index':'0','interval':'auto','sort':!('@timestamp','desc'))""",
        ),
        (
            [],
            {'time_from': '2019-07-24T12:00:00Z'},
            200,
            """https://kibana.taxi.yandex-team.ru/app/kibana#/discover?_g=('filters':!(('$state':('store':'appState'),'meta':('alias':'type','disabled':!f,'key':'query','negate':!f),'query':('query_string':('query':'type:"response"')))),'refreshInterval':('display':'Off','pause':!f,'value':0),'time':('from':'2019-07-24T15:00:00.000000','mode':'quick','to':'now'))&_a=('columns':!('_source'),'index':'0','interval':'auto','sort':!('@timestamp','desc'))""",
        ),
        (
            [
                {'name': 'type', 'value': 'routestats,launch'},
                {'name': 'driver_id', 'value': '123abc'},
            ],
            {
                'time_from': '2019-07-24T12:00:00Z',
                'time_to': '2019-07-24T13:00:00Z',
            },
            200,
            """https://kibana.taxi.yandex-team.ru/app/kibana#/discover?_g=('filters':!(('$state':('store':'appState'),'meta':('alias':'type','disabled':!f,'key':'query','negate':!f),'query':('query_string':('query':'type:"response" OR type:"periodic_task_finish"'))),('$state':('store':'appState'),'meta':('alias':'meta_type','disabled':!f,'key':'query','negate':!f),'query':('query_string':('query':'meta_type:routestats OR meta_type:launch'))),('$state':('store':'appState'),'meta':('alias':'meta_driver_id','disabled':!f,'key':'query','negate':!f),'query':('query_string':('query':'meta_driver_id:"123abc"')))),'refreshInterval':('display':'Off','pause':!f,'value':0),'time':('from':'2019-07-24T15:00:00.000000','mode':'quick','to':'2019-07-24T16:00:00.000000'))&_a=('columns':!('_source'),'index':'0','interval':'auto','sort':!('@timestamp','desc'))""",
        ),
        (
            [{'name': 'park_name', 'value': 'abc'}],
            {},
            200,
            """https://kibana.taxi.yandex-team.ru/app/kibana#/discover?_g=('filters':!(('$state':('store':'appState'),'meta':('alias':'type','disabled':!f,'key':'query','negate':!f),'query':('query_string':('query':'type:"response" OR type:"stq_task_finish" OR type:"periodic_task_finish"'))),('$state':('store':'appState'),'meta':('alias':'meta_park_id','disabled':!f,'key':'query','negate':!f),'query':('query_string':('query':'meta_park_id:"abc"')))),'refreshInterval':('display':'Off','pause':!f,'value':0),'time':('from':'now-15m','mode':'quick','to':'now'))&_a=('columns':!('_source'),'index':'0','interval':'auto','sort':!('@timestamp','desc'))""",
        ),
        (
            [{'name': 'stq_task', 'value': 'send_report'}],
            {},
            200,
            """https://kibana.taxi.yandex-team.ru/app/kibana#/discover?_g=('filters':!(('$state':('store':'appState'),'meta':('alias':'type','disabled':!f,'key':'query','negate':!f),'query':('query_string':('query':'type:"stq_task_finish" OR type:"periodic_task_finish"'))),('$state':('store':'appState'),'meta':('alias':'queue','disabled':!f,'key':'query','negate':!f),'query':('query_string':('query':'queue:"send_report"')))),'refreshInterval':('display':'Off','pause':!f,'value':0),'time':('from':'now-15m','mode':'quick','to':'now'))&_a=('columns':!('_source'),'index':'0','interval':'auto','sort':!('@timestamp','desc'))""",
        ),
        (
            [{'name': 'user_phone', 'value': '+7xxxxxxxx'}],
            {},
            200,
            """https://kibana.taxi.yandex-team.ru/app/kibana#/discover?_g=('filters':!(('$state':('store':'appState'),'meta':('alias':'type','disabled':!f,'key':'query','negate':!f),'query':('query_string':('query':'type:"response" OR type:"stq_task_finish" OR type:"periodic_task_finish"'))),('$state':('store':'appState'),'meta':('alias':'device_id, meta_user_id, personal_phone_id, phone_id','disabled':!f,'key':'query','negate':!f),'query':('query_string':('query':'phone_id:"0" OR phone_id:"1" OR phone_id:"2" OR phone_id:"3" OR phone_id:"4" OR phone_id:"5" OR phone_id:"6" OR phone_id:"7" OR phone_id:"8" OR phone_id:"9" OR personal_phone_id:"0" OR personal_phone_id:"1" OR personal_phone_id:"2" OR personal_phone_id:"3" OR personal_phone_id:"4" OR personal_phone_id:"5" OR personal_phone_id:"6" OR personal_phone_id:"7" OR personal_phone_id:"8" OR personal_phone_id:"9" OR meta_user_id:"0" OR meta_user_id:"1" OR meta_user_id:"2" OR meta_user_id:"3" OR meta_user_id:"4" OR meta_user_id:"5" OR meta_user_id:"6" OR meta_user_id:"7" OR meta_user_id:"8" OR meta_user_id:"9" OR device_id:"0" OR device_id:"1" OR device_id:"2" OR device_id:"3" OR device_id:"4" OR device_id:"5" OR device_id:"6" OR device_id:"7" OR device_id:"8" OR device_id:"9"')))),'refreshInterval':('display':'Off','pause':!f,'value':0),'time':('from':'now-15m','mode':'quick','to':'now'))&_a=('columns':!('_source'),'index':'0','interval':'auto','sort':!('@timestamp','desc'))""",
        ),
    ],
)
@pytest.mark.config(TVM_RULES=[{'src': 'eslogsadminpy3', 'dst': 'personal'}])
async def test_create_es_request(
        patch, mockserver, web_app_client, filters, params_ext, status, url,
):
    @mockserver.handler('/personal/v1/phones/find')
    def _personal_handler(request):
        return mockserver.make_response(
            status=404, json={'code': 'not-found', 'message': 'error'},
        )

    @mockserver.json_handler('/eats-notifications/v1/device-list')
    def _device_handler(request):
        return {}

    @patch('eslogadminpy3.lib.data_api.get_user_phones')
    async def _get_user_phones(*args, **kwargs):
        return [{'_id': x, 'type': 'uber'} for x in range(10)]

    @patch('eslogadminpy3.lib.data_api.get_users_by_phones')
    async def _get_users_by_phones(*args, **kwargs):
        return [{'_id': x, 'phone_id': x, 'device_id': x} for x in range(10)]

    @patch('taxi.util.cleaners.clean_international_phone')
    async def _clean_international_phone(
            territories_client, phone, *args, **kwargs,
    ):
        return phone

    response = await web_app_client.post(
        '/v2/kibana/url/', params={**params_ext}, json={'filters': filters},
    )
    assert response.status == status
    if status == 200:
        data = await response.json()
        assert data['link'] == url
