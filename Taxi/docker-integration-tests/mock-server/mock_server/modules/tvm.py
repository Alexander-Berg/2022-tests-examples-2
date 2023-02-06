import typing

from aiohttp import web


DEFAULT_KEYS = (
    '1:CpgCCpMCCAEQABqIAjCCAQQCggEAcLEXeH67FQESFUn4_7wnX7wN0PUrBoU'
    'sm3QQ4W5vC-qz6sXaEjSwnTV8w1o-z6X9KPLlhzMQvuS38NCNfK4uvJ4Zvfp3'
    'YsXJ25-rYtbnrYJHNvHohD-kPCCw_yZpMp21JdWigzQGuV7CtrxUhF-NNrsnU'
    'aJrE5-OpEWNt4X6nCItKIYeVcSK6XJUbEWbrNCRbvkSc4ak2ymFeMuHYJVjxh'
    '4eQbk7_ZPzodP0WvF6eUYrYeb42imVEOR8ofVLQWE5DVnb1z_TqZm4i1XkS7j'
    'MwZuBxBRw8DGdYei0lT_sAf7KST2jC0590NySB3vsBgWEVs1OdUUWA6r-Dvx9'
    'dsOQtSCVkQYQAAqZAgqUAggCEAAaiQIwggEFAoIBAQDhEBM5-6YsPWfogKtbl'
    'uJoCX1WV2KdzOaQ0-OlRbBzeCzw-eQKu12c8WakHBbeCMd1I1TU64SDkDorWj'
    'XGIa_2xT6N3zzNAE50roTbPCcmeQrps26woTYfYIuqDdoxYKZNr0lvNLLW47v'
    'Br7EKqo1S4KSj7aXK_XYeEvUgIgf3nVIcNrio7VTnFmGGVQCepaL1Hi1gN4yI'
    'XjVZ06PBPZ-DxSRu6xOGbFrfKMJeMPs7KOyE-26Q3xOXdTIa1X-zYIucTd_bx'
    'UCL4BVbwW2AvbbFsaG7ISmVdGu0XUTmhXs1KrEfUVLRJhE4Dx99hAZXm1_HlY'
    'MUeJcMQ_oHOhV94ENFIJaRBhACCpYBCpEBCAMQABqGATCBgwKBgF9t2YJGAJk'
    'RRFq6fWhi3m1TFW1UOE0f6ZrfYhHAkpqGlKlh0QVfeTNPpeJhi75xXzCe6oRe'
    'RUm-0DbqDNhTShC7uGUv1INYnRBQWH6E-5Fc5XrbDFSuGQw2EYjNfHy_HefHJ'
    'XxQKAqPvxBDKMKkHgV58WtM6rC8jRi9sdX_ig2NIJeRBhABCpYBCpEBCAQQAB'
    'qGATCBgwKBgGB4d6eLGUBv-Q6EPLehC4S-yuE2HB-_rJ7WkeYwyp-xIPolPrd'
    '-PQme2utHB4ZgpXHIu_OFksDe_0bPgZniNRSVRbl7W49DgS5Ya3kMfrYB4DnF'
    '5Fta5tn1oV6EwxYD4JONpFTenOJALPGTPawxXEfon_peiHOSBuQMu3_Vn-l1I'
    'JiRBhADCpcBCpIBCAUQABqHATCBhAKBgQCTJMKIfmfeZpaI7Q9rnsc29gdWaw'
    'K7TnpVKRHws1iY7EUlYROeVcMdAwEqVM6f8BVCKLGgzQ7Gar_uuxfUGKwqEQz'
    'oppDraw4F75J464-7D5f6_oJQuGIBHZxqbMONtLjBCXRUhQW5szBLmTQ_R3qa'
    'Jb5vf-h0APZfkYhq1cTttSCZkQYQBAqWAQqRAQgLEAAahgEwgYMCgYBvvGVH_'
    'M2H8qxxv94yaDYUTWbRnJ1uiIYc59KIQlfFimMPhSS7x2tqUa2-hI55JiII0X'
    'ym6GNkwLhyc1xtWChpVuIdSnbvttbrt4weDMLHqTwNOF6qAsVKGKT1Yh8yf-q'
    'b-DSmicgvFc74mBQm_6gAY1iQsf33YX8578ClhKBWHSCVkQYQAAqXAQqSAQgM'
    'EAAahwEwgYQCgYEAkuzFcd5TJu7lYWYe2hQLFfUWIIj91BvQQLa_Thln4YtGC'
    'O8gG1KJqJm-YlmJOWQG0B7H_5RVhxUxV9KpmFnsDVkzUFKOsCBaYGXc12xPVi'
    'oawUlAwp5qp3QQtZyx_se97YIoLzuLr46UkLcLnkIrp-Jo46QzYi_QHq45WTm'
    '8MQ0glpEGEAIKlwEKkgEIDRAAGocBMIGEAoGBAIUzbxOknXf_rNt17_ir8JlW'
    'vrtnCWsQd1MAnl5mgArvavDtKeBYHzi5_Ak7DHlLzuA6YE8W175FxLFKpN2hk'
    'z-l-M7ltUSd8N1BvJRhK4t6WffWfC_1wPyoAbeSN2Yb1jygtZJQ8wGoXHcJQU'
    'XiMit3eFNyylwsJFj1gzAR4JCdIJeRBhABCpYBCpEBCA4QABqGATCBgwKBgFM'
    'cbEpl9ukVR6AO_R6sMyiU11I8b8MBSUCEC15iKsrVO8v_m47_TRRjWPYtQ9eZ'
    '7o1ocNJHaGUU7qqInFqtFaVnIceP6NmCsXhjs3MLrWPS8IRAy4Zf4FKmGOx3N'
    '9O2vemjUygZ9vUiSkULdVrecinRaT8JQ5RG4bUMY04XGIwFIJiRBhADCpYBCp'
    'EBCA8QABqGATCBgwKBgGpCkW-NR3li8GlRvqpq2YZGSIgm_PTyDI2Zwfw69gr'
    'sBmPpVFW48Vw7xoMN35zcrojEpialB_uQzlpLYOvsMl634CRIuj-n1QE3-gaZ'
    'TTTE8mg-AR4mcxnTKThPnRQpbuOlYAnriwiasWiQEMbGjq_HmWioYYxFo9USl'
    'klQn4-9IJmRBhAEEpUBCpIBCAYQABqHATCBhAKBgQCoZkFGm9oLTqjeXZAq6j'
    '5S6i7K20V0lNdBBLqfmFBIRuTkYxhs4vUYnWjZrKRAd5bp6_py0csmFmpl_5Y'
    'h0b-2pdo_E5PNP7LGRzKyKSiFddyykKKzVOazH8YYldDAfE8Z5HoS9e48an5J'
    'sPg0jr-TPu34DnJq3yv2a6dqiKL9zSCakQYSlQEKkgEIEBAAGocBMIGEAoGBA'
    'Lhrihbf3EpjDQS2sCQHazoFgN0nBbE9eesnnFTfzQELXb2gnJU9enmV_aDqaH'
    'KjgtLIPpCgn40lHrn5k6mvH5OdedyI6cCzE-N-GFp3nAq0NDJyMe0fhtIRD__'
    'CbT0ulcvkeow65ubXWfw6dBC2gR_34rdMe_L_TGRLMWjDULbNIJqRBg'
)


class Application(web.Application):
    def __init__(self):
        super().__init__()
        self.router.add_post('/', self.handle_ticket_request)
        self.router.add_post('/ticket', self.handle_ticket_request)
        self.router.add_post('/2/ticket/', self.handle_tickets)
        self.router.add_post('/2/ticket', self.handle_tickets)
        self.router.add_get('/2/keys', self.handle_keys_request)
        self.router.add_get('/tvm/checksrv', self.handle_service_ticket_check)
        self.router.add_get('/tvm/tickets', self.handle_tvm_tickets)

    async def handle_ticket_request(self, _):
        return web.Response(text='tvk_ticket_mock')

    async def handle_keys_request(self, _):
        return web.Response(text=DEFAULT_KEYS)

    async def handle_tickets(self, request):
        parameters = await request.post()
        dsts = parameters.get('dst', '')
        src = parameters.get('src', '')
        if dsts:
            dst_list = dsts.split(',')
        else:
            dst_list = []
        return web.json_response(
            {dst: {'ticket': f'3:serv:{src}-{dst}'} for dst in dst_list},
            content_type='text/json',
        )

    async def handle_service_ticket_check(self, request):
        tvm_service_ticket = request.headers.get('X-Ya-Service-Ticket', '')
        parts: typing.List[str] = tvm_service_ticket.split(':')
        src, dst = parts[2].split('-')
        return web.json_response({'src': src, 'dst': dst})

    async def handle_tvm_tickets(self, request):
        dsts = request.rel_url.query['dsts']
        if dsts:
            dst_list = dsts.split(',')
        else:
            dst_list = []
        return web.json_response(
            {dst: {'ticket': DEFAULT_KEYS, 'tvm_id': dst} for dst in dst_list},
        )
