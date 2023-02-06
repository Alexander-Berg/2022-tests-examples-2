from tests_plus.utils import common


class BaseRequest:
    def __init__(self, taxi_plus):
        self.client = taxi_plus


class SubscriptionInfoRequest(BaseRequest):
    def request(self, *, subscription_id):
        return (
            common.HttpRequest(self.client.get)
            .path('/4.0/plus/v1/subscriptions/info')
            .params(subscription_id=subscription_id)
            .headers(**{'X-Yandex-UID': 'yandex_uid'})
            .headers(**{'X-Remote-IP': '185.15.98.232'})
            .headers(**{'X-Request-Language': 'en'})
            .headers(**{'X-YaTaxi-Pass-Flags': 'phonish'})
        )


class SubscriptionInfoRequestV2(BaseRequest):
    def request(self, *, subscription_id):
        return (
            common.HttpRequest(self.client.get)
            .path('/4.0/plus/v2/subscriptions/info')
            .params(subscription_id=subscription_id)
            .headers(**{'X-Yandex-UID': 'yandex_uid'})
            .headers(**{'X-Remote-IP': '185.15.98.232'})
            .headers(**{'X-Request-Language': 'en'})
            .headers(**{'X-YaTaxi-Pass-Flags': 'phonish'})
            .headers(
                **{
                    'X-Request-Application': (
                        'app_name=iphone,app_ver1=10,app_ver2=2'
                    ),
                },
            )
            .headers(**{'X-YaTaxi-PhoneId': 'phone_id'})
        )


class SubscriptionPurchaseRequest(BaseRequest):
    def request(self, *, subscription_id, payment_method_id):
        return (
            common.HttpRequest(self.client.post)
            .path('/4.0/plus/v1/subscriptions/purchase')
            .params(subscription_id=subscription_id)
            .body(payment_method_id=payment_method_id)
            .headers(**{'X-Yandex-UID': '457831'})
            .headers(**{'X-Remote-IP': '185.15.98.232'})
            .headers(**{'X-Request-Language': 'ru'})
            .headers(**{'X-YaTaxi-Pass-Flags': 'phonish'})
        )


class SubscriptionStatusRequest(BaseRequest):
    def request(self, *, purchase_id):
        return (
            common.HttpRequest(self.client.get)
            .path('/4.0/plus/v1/subscriptions/purchase')
            .params(purchase_id=purchase_id)
            .headers(**{'X-Yandex-UID': '457831'})
            .headers(**{'X-Remote-IP': '185.15.98.232'})
            .headers(**{'X-Request-Language': 'ru'})
            .headers(**{'X-YaTaxi-Pass-Flags': 'phonish'})
        )


class UidNotifyHandle(BaseRequest):
    def request(self, *, phonish_uid, portal_uid, event='bind'):
        return (
            common.HttpRequest(self.client.post)
            .path('/internal/v1/uid-notify/handle')
            .body(
                event_type=event,
                phonish_uid=phonish_uid,
                portal_uid=portal_uid,
            )
        )


class InternalListRequest(BaseRequest):
    def request(self):
        return (
            common.HttpRequest(self.client.get)
            .path('/internal/v1/subscriptions/list')
            .headers(yandex_uid='123456')
            .headers(remote_ip='185.15.98.232')
            .headers(request_language='ru')
            .headers(pass_flags='phonish')
            .headers(
                **{
                    'X-Request-Application': (
                        'app_name=iphone,app_ver1=10,app_ver2=2'
                    ),
                },
            )
            .headers(**{'X-YaTaxi-PhoneId': 'phone_id'})
        )


class SubscriptionStop(BaseRequest):
    def request(self, subscription_id):
        return (
            common.HttpRequest(self.client.post)
            .path('/4.0/plus/v1/subscriptions/stop')
            .params(subscription_id=subscription_id)
            .headers(yandex_uid='123456')
        )


class SubscriptionUpgrade(BaseRequest):
    def request(self, has_plus: bool, has_cashback_plus: bool):
        pass_flags = []
        if has_plus:
            pass_flags.append('ya-plus')
        if has_cashback_plus:
            pass_flags.append('cashback-plus')
        return (
            common.HttpRequest(self.client.post)
            .path('/4.0/plus/v1/subscriptions/upgrade')
            .headers(
                yandex_uid='123456',
                remote_ip='185.15.98.232',
                pass_flags=','.join(pass_flags),
            )
            .headers(
                **{
                    'X-Request-Application': (
                        'app_name=iphone,app_ver1=10,app_ver2=2'
                    ),
                },
            )
            .headers(**{'X-YaTaxi-PhoneId': 'phone_id'})
        )


class TotwInfo(BaseRequest):
    def request(
            self,
            order_id='default_order',
            order_cost=500,
            agent_cashback=None,
            marketing_cashback=None,
            kind='final_cost',
            order_status='complete',
            category='econom',
            currency='RUB',
            personal_wallet=None,
            pass_flags=None,
            possible_cashback=None,
            is_possible_cashback=None,
            cashback_by_sponsor=None,
            payment=None,
            cost_breakdown=None,
            fixed_price=None,
            request_application='app_name=iphone,app_ver1=0,app_ver2=0',
    ):
        complements = None
        if personal_wallet is not None:
            complements = {'personal_wallet': personal_wallet}
        current_prices = {'user_total_price': order_cost, 'kind': kind}
        if agent_cashback is not None:
            current_prices['cashback_price'] = agent_cashback
        if marketing_cashback is not None:
            current_prices['discount_cashback'] = marketing_cashback
        if possible_cashback is not None:
            current_prices['possible_cashback'] = possible_cashback
        if cashback_by_sponsor is not None:
            current_prices['cashback_by_sponsor'] = cashback_by_sponsor
        if cost_breakdown:
            current_prices['cost_breakdown'] = cost_breakdown
        if pass_flags is None:
            pass_flags = []
        return (
            common.HttpRequest(self.client.post)
            .path('/internal/v2/taxiontheway/info')
            .params(order_cost=order_cost)
            .headers(yandex_uid='123456')
            .headers(remote_ip='185.15.98.232')
            .headers(request_language='en')
            .headers(pass_flags=','.join(pass_flags))
            .headers(x_request_application=request_application)
            .body(
                order_id=order_id,
                order_status=order_status,
                currency=currency,
                category=category,
                current_prices=current_prices,
                complements=complements,
                is_possible_cashback=is_possible_cashback,
                payment=payment,
                fixed_price=fixed_price,
            )
        )


class Country(BaseRequest):
    def request(self, ipaddress):
        return (
            common.HttpRequest(self.client.get)
            .path('/internal/v1/country')
            .headers(remote_ip=ipaddress)
        )
