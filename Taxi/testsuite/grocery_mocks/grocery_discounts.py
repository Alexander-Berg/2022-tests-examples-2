import pytest

SUPPORTED_DISCOUNT_HIERARCHIES = [
    'menu_discounts',
    'menu_cashback',
    'dynamic_discounts',
    'suppliers_discounts',
    'cart_discounts',
    'cart_cashback',
    'payment_method_discounts',
    'payment_method_cashback',
    'markdown_discounts',
    'bundle_discounts',
]

FETCHED_HIERARCHIES = {
    'menu_discounts',
    'bundle_discounts',
    'menu_cashback',
    'bundle_cashback',
}


@pytest.fixture(name='grocery_discounts')
def mock_grocery_discounts(mockserver):
    product_id = 'product_1'
    discount_obj = {'menu_value': {'value_type': 'fraction', 'value': '10.00'}}
    pm_discount_meta_obj = {
        'type': 'mastercard',
        'description_template_tanker_key': 'test_mastercard_discount',
    }
    match_result_menu = {
        'discounts': [
            {
                'discount': {
                    'active_with_surge': False,
                    'money_value': discount_obj,
                },
            },
        ],
        'hierarchy_name': 'menu_discounts',
        'status': 'ok',
    }
    match_result_cart = {
        'discounts': [],
        'hierarchy_name': 'cart_discounts',
        'status': 'ok',
    }
    match_result_payment_method = {
        'discounts': [
            {
                'discount': {
                    'active_with_surge': False,
                    'money_value': discount_obj,
                    'discount_meta': pm_discount_meta_obj,
                },
            },
        ],
        'hierarchy_name': 'payment_method_discounts',
        'status': 'ok',
    }
    subqueries = {
        product_id: {
            'menu_discounts': match_result_menu,
            'cart_discounts': match_result_cart,
            'payment_method_discounts': match_result_payment_method,
        },
    }
    fetched_products = {}
    discount_informers = {}

    class Context:
        def __init__(self):
            self.response = {}
            self.on_v4_match_discounts = None
            self.on_v3_fetch_discounts = None
            self.on_v4_fetch_discounted_products = None
            self.on_v3_fetch_informers = None

        def set_v4_match_discounts_check(self, *, on_v4_match_discounts):
            self.on_v4_match_discounts = on_v4_match_discounts

        def set_v3_fetch_discounts_check(self, *, on_v3_fetch_discounts):
            self.on_v3_fetch_discounts = on_v3_fetch_discounts

        # pylint: disable=invalid-name
        def set_v4_fetch_discounted_products_check(
                self, *, on_v4_fetch_discounted_products,
        ):
            self.on_v4_fetch_discounted_products = (
                on_v4_fetch_discounted_products
            )

        def set_v3_fetch_informers_check(self, *, on_v3_fetch_informers):
            self.on_v3_fetch_informers = on_v3_fetch_informers

        def add_fetched_product(
                self,
                *,
                product_id,
                hierarchy_name,
                discount_meta=None,
                is_subcategory=False,
        ):
            if hierarchy_name not in fetched_products:
                fetched_products[hierarchy_name] = {
                    'groups': [],
                    'products': [],
                    **(
                        {}
                        if not discount_meta
                        else {
                            'is_price_strikethrough': discount_meta.get(
                                'is_price_strikethrough', None,
                            ),
                            'is_expiring': discount_meta.get('false', None),
                        }
                    ),
                }
            if is_subcategory:
                fetched_products[hierarchy_name]['groups'].append(
                    {'group_name': product_id},
                )
            else:
                fetched_products[hierarchy_name]['products'].append(product_id)

        def add_money_discount(
                self,
                *,
                product_id,
                value_type,
                value,
                hierarchy_name='menu_discounts',
                discount_meta=None,
                draft_id=None,
                is_subcategory=False,
                maximum_discount=None,
                discount_id=None,
                has_discount_usage_restrictions=None,
        ):
            self.add_complex_discount(
                product_id=product_id,
                money_value_type=value_type,
                money_value=value,
                hierarchy_name=hierarchy_name,
                discount_meta=discount_meta,
                draft_id=draft_id,
                is_subcategory=is_subcategory,
                maximum_money_discount=maximum_discount,
                discount_id=discount_id,
                has_discount_usage_restrictions=(
                    has_discount_usage_restrictions
                ),
            )

        def add_bundle_discount(
                self,
                *,
                product_id,
                discount_value,
                bundle,
                hierarchy_name='menu_discounts',
                discount_meta=None,
                draft_id=None,
                is_subcategory=False,
                discount_id=None,
                has_discount_usage_restrictions=None,
        ):
            self.add_complex_discount(
                product_id=product_id,
                bundle_discount_value=discount_value,
                bundle=bundle,
                hierarchy_name=hierarchy_name,
                discount_meta=discount_meta,
                draft_id=draft_id,
                is_subcategory=is_subcategory,
                discount_id=discount_id,
                has_discount_usage_restrictions=(
                    has_discount_usage_restrictions
                ),
            )

        def add_cashback_discount(
                self,
                *,
                product_id,
                value_type,
                value,
                hierarchy_name='menu_cashback',
                draft_id=None,
                discount_meta=None,
                is_subcategory=False,
                maximum_discount=None,
                discount_id=None,
                has_discount_usage_restrictions=None,
        ):
            self.add_complex_discount(
                product_id=product_id,
                cashback_value_type=value_type,
                cashback_value=value,
                hierarchy_name=hierarchy_name,
                discount_meta=discount_meta,
                draft_id=draft_id,
                is_subcategory=is_subcategory,
                maximum_cashback_discount=maximum_discount,
                discount_id=discount_id,
                has_discount_usage_restrictions=(
                    has_discount_usage_restrictions
                ),
            )

        def add_complex_discount(
                self,
                *,
                product_id,
                bundle_discount_value=None,
                bundle=None,
                money_value_type=None,
                money_value=None,
                maximum_money_discount=None,
                cashback_value_type=None,
                cashback_value=None,
                maximum_cashback_discount=None,
                hierarchy_name='menu_discounts',
                discount_meta=None,
                draft_id=None,
                is_subcategory=False,
                discount_id=None,
                has_discount_usage_restrictions=None,
        ):
            is_money_payment = (
                money_value_type is not None and money_value is not None
            )
            is_cashback_payment = (
                cashback_value_type is not None and cashback_value is not None
            )
            is_product_payment = (
                bundle_discount_value is not None and bundle is not None
            )
            assert (
                is_product_payment or is_money_payment or is_cashback_payment
            )

            if hierarchy_name in FETCHED_HIERARCHIES:
                self.add_fetched_product(
                    product_id=product_id,
                    hierarchy_name=hierarchy_name,
                    discount_meta=discount_meta,
                    is_subcategory=is_subcategory,
                )

            draft_id_meta = {}
            if draft_id:
                draft_id_meta['create_draft_id'] = draft_id

            discount_extra_meta = {}
            if discount_id:
                discount_extra_meta['discount_id'] = discount_id
            if has_discount_usage_restrictions is not None:
                discount_extra_meta[
                    'has_discount_usage_restrictions'
                ] = has_discount_usage_restrictions

            money_value_payment = {}
            if is_money_payment:
                money_value_payment = {
                    'money_value': {
                        'menu_value': {
                            'value_type': money_value_type,
                            'value': money_value,
                            **(
                                {'maximum_discount': maximum_money_discount}
                                if maximum_money_discount is not None
                                else {}
                            ),
                            **discount_extra_meta,
                        },
                    },
                }

            cashback_value_payment = {}
            if is_cashback_payment:
                cashback_value_payment = {
                    'cashback_value': {
                        'menu_value': {
                            'value_type': cashback_value_type,
                            'value': cashback_value,
                            **(
                                {'maximum_discount': maximum_cashback_discount}
                                if maximum_cashback_discount is not None
                                else {}
                            ),
                            **discount_extra_meta,
                        },
                    },
                }

            product_value_payment = {}
            if is_product_payment:
                product_value_payment = {
                    'product_value': {
                        'discount_value': bundle_discount_value,
                        'bundle': bundle,
                        **discount_extra_meta,
                    },
                }

            if product_id not in subqueries:
                subqueries[product_id] = {}

            if hierarchy_name not in subqueries[product_id]:
                subqueries[product_id][hierarchy_name] = {
                    'discounts': [
                        {
                            **draft_id_meta,
                            'discount': {
                                'active_with_surge': True,
                                **money_value_payment,
                                **cashback_value_payment,
                                **product_value_payment,
                                'discount_meta': discount_meta,
                                **discount_extra_meta,
                            },
                        },
                    ],
                    'hierarchy_name': hierarchy_name,
                    'status': 'ok',
                }
            else:
                subqueries[product_id][hierarchy_name]['discounts'].append(
                    {
                        **draft_id_meta,
                        'discount': {
                            'active_with_surge': True,
                            **money_value_payment,
                            **cashback_value_payment,
                            **product_value_payment,
                            'discount_meta': discount_meta,
                            **discount_extra_meta,
                        },
                    },
                )

        def add_cart_discount(
                self,
                *,
                product_id,
                table_items,
                draft_id=None,
                type_value,
                discount_id=None,
                has_discount_usage_restrictions=None,
                hierarchy_name='cart_discounts',
        ):
            value = {'cart_value': {'value': table_items}}
            draft_id_meta = {}
            if draft_id:
                draft_id_meta['create_draft_id'] = draft_id
            discount_extra_meta = {}
            if discount_id:
                discount_extra_meta['discount_id'] = discount_id
            if has_discount_usage_restrictions is not None:
                discount_extra_meta[
                    'has_discount_usage_restrictions'
                ] = has_discount_usage_restrictions

            if product_id not in subqueries:
                subqueries[product_id] = {}

            if hierarchy_name not in subqueries[product_id]:
                subqueries[product_id][hierarchy_name] = {
                    'discounts': [
                        {
                            **draft_id_meta,
                            'discount': {
                                'active_with_surge': True,
                                type_value: value,
                                **discount_extra_meta,
                            },
                        },
                    ],
                    'hierarchy_name': hierarchy_name,
                    'status': 'ok',
                }
            else:
                subqueries[product_id][hierarchy_name]['discounts'].append(
                    {
                        **draft_id_meta,
                        'discount': {
                            'active_with_surge': True,
                            type_value: value,
                            **discount_extra_meta,
                        },
                    },
                )

        def add_cart_money_discount(
                self,
                *,
                product_id,
                table_items,
                draft_id=None,
                discount_id=None,
                has_discount_usage_restrictions=None,
        ):
            self.add_cart_discount(
                product_id=product_id,
                table_items=table_items,
                draft_id=draft_id,
                type_value='money_value',
                discount_id=discount_id,
                has_discount_usage_restrictions=(
                    has_discount_usage_restrictions
                ),
            )

        def add_cart_cashback_gain(
                self,
                *,
                product_id,
                table_items,
                draft_id=None,
                discount_id=None,
                has_discount_usage_restrictions=None,
                hierarchy_name='cart_discounts',
        ):
            self.add_cart_discount(
                product_id=product_id,
                table_items=table_items,
                draft_id=draft_id,
                type_value='cashback_value',
                discount_id=discount_id,
                has_discount_usage_restrictions=(
                    has_discount_usage_restrictions
                ),
                hierarchy_name=hierarchy_name,
            )

        def add_informer(
                self,
                *,
                hierarchy_name=None,
                text=None,
                picture=None,
                color=None,
        ):
            if not hierarchy_name:
                hierarchy_name = 'menu_discounts'
            if not text:
                text = 'default text'
            if not picture:
                picture = 'default picture'
            if not color:
                color = 'default colot'
            if hierarchy_name not in discount_informers:
                discount_informers[hierarchy_name] = []
            discount_informers[hierarchy_name].append(
                {'text': text, 'picture': picture, 'color': color},
            )

        @property
        def last_match_discounts_response(self):
            return self.response

        @property
        def times_called(self):
            return _mock_match_discounts.times_called

    ctx = Context()

    def has_payment_method_and_card_bin(body):
        has_card_bin = bool(body['common_conditions'].get('card_bins', []))
        has_payment_method = bool(
            body['common_conditions'].get('payment_methods', []),
        )
        return has_payment_method and has_card_bin

    @mockserver.json_handler('/grocery-discounts/v4/match-discounts')
    def _mock_match_discounts(request):
        if ctx.on_v4_match_discounts:
            assert ctx.on_v4_match_discounts(request.headers, request.json)

        body = request.json
        match_results = []

        for subquery in request.json['subqueries']:
            subquery_id = subquery['subquery_id']
            requested_product = subquery['conditions']['product']
            if requested_product not in subqueries:
                continue

            results = []
            for hierarchy in SUPPORTED_DISCOUNT_HIERARCHIES:
                if (
                        hierarchy not in subqueries[requested_product]
                        or hierarchy not in body['hierarchy_names']
                ):
                    continue

                if hierarchy == 'payment_method_discounts':
                    if has_payment_method_and_card_bin(body):
                        results.append(
                            subqueries[requested_product][hierarchy],
                        )
                else:
                    results.append(subqueries[requested_product][hierarchy])

            match_results.append(
                {'subquery_id': subquery_id, 'results': results},
            )

        ctx.response = {'match_results': match_results}
        return ctx.response

    @mockserver.json_handler('/grocery-discounts/v3/fetch-discounts')
    def _mock_fetch_discounts(request):
        if ctx.on_v3_fetch_discounts:
            assert ctx.on_v3_fetch_discounts(request.headers, request.json)

        results = []
        for hierarchy_name in request.json['hierarchy_names']:
            if hierarchy_name not in SUPPORTED_DISCOUNT_HIERARCHIES:
                continue
            if (
                    hierarchy_name == 'payment_method_discounts'
                    and not has_payment_method_and_card_bin(request.json)
            ):
                continue

            hierarchy_discounts = []
            for subquery_id, discounts_info in subqueries.items():
                if hierarchy_name not in discounts_info:
                    continue

                for discount in discounts_info[hierarchy_name]['discounts']:
                    hierarchy_discounts.append(
                        {
                            **discount,
                            'match_path': [
                                {
                                    'condition_name': (
                                        'label'
                                        if hierarchy_name
                                        == 'dynamic_discounts'
                                        else 'product'
                                    ),
                                    'value': subquery_id,
                                },
                            ],
                        },
                    )
            results.append(
                {
                    'status': 'ok',
                    'discounts': hierarchy_discounts,
                    'hierarchy_name': hierarchy_name,
                },
            )
        return {'match_results': results}

    @mockserver.json_handler('/grocery-discounts/v4/fetch-discounted-products')
    def _mock_v4_fetch_discounted_products(request):
        if ctx.on_v4_fetch_discounted_products:
            assert ctx.on_v4_fetch_discounted_products(
                request.headers, request.json,
            )

        items = []
        for key, value in fetched_products.items():
            if key in request.json['hierarchy_names']:
                items.append({'hierarchy_name': key, **value})
        return {'items': items}

    @mockserver.json_handler('/grocery-discounts/v3/fetch-informers')
    def _mock_v3_fetch_informers(request):
        if ctx.on_v3_fetch_informers:
            assert ctx.on_v3_fetch_informers(request.headers, request.json)

        body = request.json
        informers = []
        for hierarchy_name in body['hierarchy_names']:
            if hierarchy_name not in discount_informers:
                continue
            for informer in discount_informers[hierarchy_name]:
                informers.append(
                    {'hierarchy_name': hierarchy_name, 'informer': informer},
                )
        return mockserver.make_response(
            json={'informers': informers}, status=200,
        )

    return ctx
