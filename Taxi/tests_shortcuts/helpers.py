import collections
import copy
import enum
import typing

from tests_shortcuts import consts


def _validate_shortcut_ids(ids):
    if len(set(ids)) != len(ids):
        bad_ids = [
            id_ for id_, count in collections.Counter(ids).items() if count > 1
        ]
        raise ValueError(f'Non-unique shortcut_ids detected: {bad_ids}')


def make_default_payload(cells=None):
    cells = [] if cells is None else cells
    _validate_shortcut_ids([cell['shortcut']['id'] for cell in cells])
    return {'grid': {'id': 'id', 'width': 2, 'cells': cells}}


def make_payload_with_shortcuts(
        shortcuts,
        blocks=None,
        supported_sections=None,
        supported_actions=None,
):
    _validate_shortcut_ids([s['id'] for s in shortcuts])
    payload = make_default_payload()
    payload['grid'].update(
        {
            'cells': [
                {'height': 2, 'width': 2, 'shortcut': copy.deepcopy(s)}
                for s in shortcuts
            ],
        },
    )
    if blocks is not None:
        payload['grid']['blocks'] = blocks
    if supported_sections or supported_actions:
        payload.update({'shortcuts': {}})
    if supported_sections is not None:
        payload['shortcuts'].update({'supported_sections': supported_sections})
    if supported_actions is not None:
        payload['shortcuts'].update({'supported_actions': supported_actions})
    return payload


def _make_badge_properties_dict(
        text, tanker_key, shape, text_color, background,
):
    return {key: value for key, value in locals().items() if value is not None}


def make_default_badge(
        text=None,
        tanker_key=None,
        shape='bubble',
        text_color='badge_text_color',
        background_color='badge_background_color',
):
    background_color = (
        {'color': background_color} if background_color else None
    )
    return _make_badge_properties_dict(
        text, tanker_key, shape, text_color, background_color,
    )


def make_overridden_badge(
        text=None,
        tanker_key=None,
        shape=None,
        text_color=None,
        background_color=None,
):
    background_color = (
        {'color': background_color} if background_color else None
    )
    return {
        '1': _make_badge_properties_dict(
            text, tanker_key, shape, text_color, background_color,
        ),
    }


@enum.unique
class Scenarios(enum.Enum):
    def _generate_next_value_(  # pylint: disable=no-self-argument
            name, start, count, last_values,
    ):
        return name

    taxi_route_input = enum.auto()
    eats_based_eats = enum.auto()
    eats_based_grocery = enum.auto()
    eats_based_pharmacy = enum.auto()
    eats_based_shop = enum.auto()
    native_shop = enum.auto()
    header_delivery = enum.auto()
    taxi_header_delivery = (
        enum.auto()
    )  # not a scenario but native appearance of scenario
    discovery_masstransit = enum.auto()
    discovery_drive = enum.auto()
    discovery_shuttle = enum.auto()
    discovery_scooters = enum.auto()
    discovery_restaurants = enum.auto()
    discovery_contacts = enum.auto()
    taxi_header_ultima = enum.auto()
    eats_shop = enum.auto()
    city_mode = enum.auto()
    market = enum.auto()

    @classmethod
    def get_all_names(cls) -> typing.List[str]:
        return [scenario.name for scenario in cls]

    @classmethod
    def get_all_except(cls, exceptions) -> typing.List['Scenarios']:
        return [scenario for scenario in cls if scenario not in exceptions]


def get_action_by_scenario(scenario, typed=False, custom=False):
    if scenario == Scenarios.taxi_header_delivery:
        return (
            consts.TYPED_NATIVE_DELIVERY_ACTION
            if typed
            else consts.NATIVE_DELIVERY_ACTION
        )
    if scenario == Scenarios.discovery_masstransit:
        # always typed
        return consts.TYPED_MASSTRANSIT_ACTION
    if scenario == Scenarios.discovery_shuttle:
        # always typed
        return consts.TYPED_SHUTTLE_ACTION
    if scenario == Scenarios.discovery_drive:
        # always typed
        return consts.TYPED_DRIVE_ACTION
    if scenario == Scenarios.discovery_scooters:
        # always typed
        return consts.TYPED_SCOOTERS_ACTION
    if scenario == Scenarios.discovery_restaurants:
        # always typed
        return consts.TYPED_RESTAURANTS_ACTION
    if scenario == Scenarios.discovery_contacts:
        # always typed
        return consts.TYPED_CONTACTS_ACTION
    if scenario == Scenarios.taxi_header_ultima:
        return consts.TYPED_ULTIMA_ACTION if typed else consts.ULTIMA_ACTION
    if scenario == Scenarios.taxi_route_input:
        return consts.TYPED_TAXI_ROUTE_INPUT_ACTION if typed else {}
    if scenario == Scenarios.market:
        action = {'name': 'market', 'type': 'shortcuts_screen'}
        return {'action': action} if custom else action
    if scenario == Scenarios.native_shop:
        action = {'name': 'shops', 'type': 'shortcuts_screen'}
        return {'action': action} if custom else action
    return consts.TYPED_DEEPLINK_ACTION if typed else consts.DEEPLINK_ACTION


def generate_brick_appearance(
        overrides=None, scenario=None, with_attributed_title=False,
):
    if overrides is None:
        overrides = {}
    value = {
        **consts.DEFAULT_APPEARANCE,
        **get_action_by_scenario(scenario, custom=True),
        **overrides,
    }
    if with_attributed_title:
        value['attributed_title'] = consts.DEFAULT_ATTRIBUTED_TITLE
    return value


def build_header_request(
        client_support,
        availability_support,
        grid_id=None,
        known_orders=None,
        multicolor_service_icons_supported=None,
        position=None,
        supported_actions=None,
        supported_sections=None,
        cells=None,
        shop_shortcuts=None,
        user_phone_info=None,
        seen=None,
        eats_promo_tags=None,
        lavka_promo_tags=None,
        market_promo_tags=None,
        supported_icon_sizes=None,
        state=None,
):
    if cells is None:
        cells = []
    request = {
        'services_availability': availability_support,
        'shortcuts': {'supported_features': client_support},
        'grid': {'id': grid_id or 'grid-id', 'width': 6, 'cells': cells},
    }
    if known_orders:
        request['known_orders'] = known_orders
    if position:
        request['position'] = position
    if multicolor_service_icons_supported is not None:
        request['shortcuts'][
            'multicolor_service_icons_supported'
        ] = multicolor_service_icons_supported
    if supported_actions:
        request['shortcuts']['supported_actions'] = supported_actions
    if supported_sections:
        request['shortcuts']['supported_sections'] = supported_sections
    if shop_shortcuts is not None:
        request['shop_shortcuts'] = shop_shortcuts
    if user_phone_info is not None:
        request['user_phone_info'] = user_phone_info
    if seen is not None:
        request['seen'] = seen
    if eats_promo_tags is not None:
        request['eats_promo_tags'] = eats_promo_tags
    if lavka_promo_tags is not None:
        request['lavka_promo_tags'] = lavka_promo_tags
    if market_promo_tags is not None:
        request['market_promo_tags'] = market_promo_tags
    if supported_icon_sizes is not None:
        request['shortcuts']['supported_icon_sizes'] = supported_icon_sizes
    if state is not None:
        request['state'] = state
    return request


class ScenarioSupport:
    def __init__(
            self,
            available_scenarios: typing.Optional[
                typing.List[Scenarios]
            ] = None,
            show_disabled_services: typing.Optional[typing.List[str]] = None,
            available_services: typing.Optional[typing.Set[str]] = None,
            deathflag_services: typing.Optional[typing.Set[str]] = None,
            service_to_deathflag_map: typing.Optional[
                typing.Dict[str, bool]
            ] = None,
    ):
        self.ordered_available_scenarios = available_scenarios or list()
        self.show_disabled_services = show_disabled_services or list()
        self.deathflag_services = deathflag_services or set()
        self.available_services = available_services
        self.service_to_deathflag_map = service_to_deathflag_map or dict()

    @property
    def available_scenarios(self):
        return set(self.ordered_available_scenarios)

    def __contains__(self, item):
        return item in self.available_scenarios

    def __to_namevalue(self):
        return {scenario.name: (scenario in self) for scenario in Scenarios}

    def to_client_support(self):
        supported_features = []
        if Scenarios.taxi_route_input in self:
            supported_features.append(
                {'type': 'taxi:route-input', 'prefetch_strategies': []},
            )
        if Scenarios.header_delivery in self:
            supported_features.append(
                {'type': 'header-deeplink', 'prefetch_strategies': []},
            )
        if Scenarios.taxi_header_delivery in self:
            supported_features.append(
                {
                    'type': 'taxi:header-summary-redirect',
                    'prefetch_strategies': [],
                },
            )
        discovery_scenarios = [
            Scenarios.discovery_drive,
            Scenarios.discovery_masstransit,
            Scenarios.discovery_scooters,
            Scenarios.discovery_restaurants,
            Scenarios.discovery_shuttle,
        ]
        if any(scenario in self for scenario in discovery_scenarios):
            supported_features.append(
                {'type': 'header-action-driven', 'prefetch_strategies': []},
            )

        eats_based_services = []
        if Scenarios.eats_based_eats in self:
            eats_based_services.append('eats')
        if Scenarios.eats_based_grocery in self:
            eats_based_services.append('grocery')
        if Scenarios.eats_based_pharmacy in self:
            eats_based_services.append('pharmacy')
        if Scenarios.eats_based_shop in self:
            eats_based_services.append('shop')
        if Scenarios.market in self:
            eats_based_services.append('market')

        if eats_based_services:
            supported_features.append(
                {
                    'type': 'eats-based:superapp',
                    'services': eats_based_services,
                    'prefetch_strategies': [],
                },
            )

        return supported_features

    def to_services_availability(self):
        modes = [
            # Hardcode taxi availability since it is hardcoded in code
            {
                'mode': 'taxi',
                'parameters': {
                    'product_tag': 'taxi',
                    'available': True,
                    'show_disabled': False,
                },
            },
        ]
        for scenario, service_name in [
                (Scenarios.eats_based_eats, 'eats'),
                (Scenarios.eats_based_grocery, 'grocery'),
                (Scenarios.eats_based_pharmacy, 'pharmacy'),
                (Scenarios.eats_based_shop, 'shop'),
                (Scenarios.discovery_drive, 'drive'),
                (Scenarios.discovery_masstransit, 'masstransit'),
                (Scenarios.discovery_scooters, 'scooters'),
                (Scenarios.discovery_restaurants, 'restaurants'),
                (Scenarios.discovery_shuttle, 'shuttle'),
                (Scenarios.discovery_contacts, 'contacts'),
                (Scenarios.market, 'market'),
        ]:
            show_disabled = service_name in self.show_disabled_services
            deathflag = service_name in self.deathflag_services
            available = scenario in self

            if self.available_services is not None:
                available = (
                    service_name in self.available_services and not deathflag
                )

            mode = {
                'mode': service_name,
                'parameters': {
                    'available': available,
                    'deathflag': deathflag,
                    'product_tag': service_name,
                    'show_disabled': show_disabled,
                },
            }

            if scenario == Scenarios.discovery_drive:
                mode['parameters'].update({'is_registered': True})

            if service_name in self.service_to_deathflag_map:
                deathflag = self.service_to_deathflag_map[service_name]
                mode['parameters']['deathflag'] = deathflag

            modes.append(mode)

        return {'modes': modes, 'products': []}

    def to_header_params_experiment(self, layout_options=None, show_from=6):
        priority = [
            scenario.name
            for scenario in self.ordered_available_scenarios
            if scenario != Scenarios.taxi_header_delivery
        ]

        if layout_options is None:
            # if no layout specified, generate layout where each service is 1
            layout_options = {k: [1] * k for k in range(1, len(priority) + 1)}
        return {
            'bricks': {
                'layout_options': layout_options,
                'priority': priority,
                'enabled': True,
            },
            'buttons': {
                'enabled': True,
                'show_from': show_from,
                'priority': priority,
            },
        }


# Cherry-picked testing environment with specific availability support
class EnvSetup:
    def __init__(
            self,
            show_disabled_services=None,
            disabled_available_scenarios=None,
            available_services=None,
    ):
        if show_disabled_services is None:
            show_disabled_services = []

        if disabled_available_scenarios is None:
            disabled_available_scenarios = set()

        # Client supports everything except pharmacy
        self.client_support = ScenarioSupport(
            available_scenarios=Scenarios.get_all_except(
                {Scenarios.eats_based_pharmacy},
            ),
        ).to_client_support()

        self.availability_support = ScenarioSupport(
            available_scenarios=Scenarios.get_all_except(
                disabled_available_scenarios,
            ),
            show_disabled_services=show_disabled_services,
            available_services=available_services,
        ).to_services_availability()

        # Layout supports everything
        self.header_params_experiment = ScenarioSupport(
            available_scenarios=list(Scenarios),
        ).to_header_params_experiment()

        self.all_supported_actions = [
            {'type': 'deeplink'},
            {'type': 'taxi:summary-redirect'},
            {
                'type': 'discovery',
                'modes': ['masstransit', 'drive', 'scooters', 'shuttle'],
            },
            {'type': 'taxi:route-input'},
            {'type': 'shortcuts_screen'},
            {
                'type': 'city_mode',
                'modes': ['drive', 'masstransit', 'scooters'],
            },
            {'type': 'scooters_qr_scan'},
            {'type': 'delivery_dashboard'},
        ]

        self.all_supported_sections = [
            {'type': 'header_linear_grid'},
            {'type': 'items_linear_grid'},
            {'type': 'buttons_container'},
        ]


def exp_create_eq_predicate(arg_name, value, arg_type='string'):
    return {
        'init': {'arg_name': arg_name, 'arg_type': arg_type, 'value': value},
        'type': 'eq',
    }


def exp_create_contains_predicate(arg_name, value, arg_type='string'):
    return {
        'init': {
            'arg_name': arg_name,
            'set_elem_type': arg_type,
            'value': value,
        },
        'type': 'contains',
    }


def create_user_phone_info(created=None, total=None):
    user_phone_info = {}

    if created is not None:
        user_phone_info['created'] = created
    if total is not None:
        user_phone_info['stat'] = {'total': total}

    return user_phone_info


def create_onboarding(counter_id, enable_in_bricks=None):
    onboarding = {
        'action': {'media': {'promo_id': 'some_promo_id'}},
        'show_policy': {
            'id': counter_id,
            'max_show_count': 3,
            'max_usage_count': 1,
        },
    }
    if enable_in_bricks is not None:
        onboarding['enable_in_bricks'] = enable_in_bricks
    return onboarding
