import typing as tp

from test_abt import utils


async def _default_response_parser(response):
    return await response.json()


def create_invoke(
        method: str,
        endpoint: str,
        taxi_abt_web,
        req_func: tp.Optional[tp.Callable] = None,
        resp_parser: tp.Optional[tp.Callable] = None,
        default_params: tp.Union[utils.Sentinel, dict] = utils.Sentinel(),
        default_body: tp.Union[utils.Sentinel, dict] = utils.Sentinel(),
):
    req_func = req_func or getattr(taxi_abt_web, method)
    resp_parser = resp_parser or _default_response_parser

    async def _inner(
            *,
            body=utils.Sentinel(),
            params=utils.Sentinel(),
            expected_code=200,
    ):
        kwargs = {}

        if not isinstance(body, utils.Sentinel):
            kwargs['json'] = body
        elif not isinstance(default_body, utils.Sentinel):
            kwargs['json'] = default_body

        if not isinstance(params, utils.Sentinel):
            kwargs['params'] = params
        elif not isinstance(default_params, utils.Sentinel):
            kwargs['params'] = default_params

        response = await req_func(endpoint, **kwargs)

        assert response.status == expected_code, (
            f'response status ({response.status}) != '
            f'expected_code ({expected_code}). '
            f'Params: {params}, body: {body}. '
            f'Response text: {await resp_parser(response)}'
        )

        return await resp_parser(response)

    return _inner
