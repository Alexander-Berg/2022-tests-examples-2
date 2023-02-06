from mock_server import host_application
from mock_server.modules import admin_pipeline
from mock_server.modules import antifraud
from mock_server.modules import archive_api
from mock_server.modules import billing
from mock_server.modules import billing_replication
from mock_server.modules import blocklist
from mock_server.modules import bunker
from mock_server.modules import card_antifraud
from mock_server.modules import cargo_claims
from mock_server.modules import cargo_corp
from mock_server.modules import checkprovider_edadeal
from mock_server.modules import classifier
from mock_server.modules import clownductor
from mock_server.modules import clowny_balancer
from mock_server.modules import conductor
from mock_server.modules import contractor_order_history
from mock_server.modules import contractor_transport
from mock_server.modules import corp_billing
from mock_server.modules import corp_integration_api
from mock_server.modules import crons
from mock_server.modules import deptrans_driver_status
from mock_server.modules import discounts
from mock_server.modules import dispatch_settings
from mock_server.modules import distlocks
from mock_server.modules import driver_login
from mock_server.modules import driver_profiles
from mock_server.modules import driver_weariness
from mock_server.modules import eater_authorizer
from mock_server.modules import eats_delivery_price
from mock_server.modules import eats_eta
from mock_server.modules import eats_order_send
from mock_server.modules import eats_order_stats
from mock_server.modules import eats_payment_methods_availability
from mock_server.modules import eats_picker_payment
from mock_server.modules import eats_plus
from mock_server.modules import eats_products
from mock_server.modules import eats_smart_prices
from mock_server.modules import eats_tags
from mock_server.modules import eda_candidates
from mock_server.modules import eda_core
from mock_server.modules import eda_surge_calculator
from mock_server.modules import elasticsearch
from mock_server.modules import experiments3
from mock_server.modules import ext_drivematics
from mock_server.modules import extjams
from mock_server.modules import fleet_rent
from mock_server.modules import geoareas
from mock_server.modules import grocery_checkins
from mock_server.modules import grocery_depots
from mock_server.modules import grocery_surge
from mock_server.modules import individual_tariffs
from mock_server.modules import lbsproxy
from mock_server.modules import logistic_dispatcher
from mock_server.modules import mds
from mock_server.modules import mockserver
from mock_server.modules import passport
from mock_server.modules import passport_internal
from mock_server.modules import payments_eda
from mock_server.modules import personal
from mock_server.modules import pickuppoints
from mock_server.modules import pricing_data_preparer
from mock_server.modules import pricing_taximeter
from mock_server.modules import processing
from mock_server.modules import quality_control
from mock_server.modules import quality_control_cpp
from mock_server.modules import replication
from mock_server.modules import saturn
from mock_server.modules import searchmaps
from mock_server.modules import selfemployed_fns_replica
from mock_server.modules import special_zones
from mock_server.modules import statistics
from mock_server.modules import suggest_maps
from mock_server.modules import superapp_misc
from mock_server.modules import surge_calculator
from mock_server.modules import taximeter
from mock_server.modules import tinkoff_secured
from mock_server.modules import transactions_eda
from mock_server.modules import tvm
from mock_server.modules import uber_token
from mock_server.modules import umlaas_eats
from mock_server.modules import user_api
from mock_server.modules import user_state
from mock_server.modules import yagr
from mock_server.modules import yamaps_router
from mock_server.modules import yt


def get_application():
    app = host_application.HostApplication()
    billing_app = billing.Application()
    passport_app = passport.Application()
    eda_core_app = eda_core.Application()
    app.add_host_app('addrs.yandex.net', searchmaps.Application())
    app.add_host_app('antifraud.taxi.yandex.net', antifraud.Application())
    app.add_host_app('archive-api.taxi.yandex.net', archive_api.Application())
    app.add_host_app('crons.taxi.yandex.net', crons.Application())
    app.add_host_app(
        'clowny-balancer.taxi.yandex.net', clowny_balancer.Application(),
    )
    app.add_host_app('balance-simple.yandex.net', billing_app)
    app.add_host_app(
        'billing-replication.taxi.yandex.net',
        billing_replication.Application(),
    )
    app.add_host_app('b2b.taxi.yandex.net', cargo_claims.Application())
    app.add_host_app(
        'card-antifraud.taxi.yandex.net', card_antifraud.Application(),
    )
    app.add_host_app(
        'corp-billing.taxi.yandex.net', corp_billing.Application(),
    )
    app.add_host_app(
        'corp-integration-api.taxi.yandex.net',
        corp_integration_api.Application(),
    )
    app.add_host_app('classifier.taxi.yandex.net', classifier.Application())
    app.add_host_app('clownductor.taxi.yandex.net', clownductor.Application())
    app.add_host_app(
        'contractor-transport.taxi.yandex.net',
        contractor_transport.Application(),
    )
    app.add_host_app(
        'deptrans-driver-status.taxi.yandex.net',
        deptrans_driver_status.Application(),
    )
    app.add_host_app(
        'dispatch-settings.taxi.yandex.net', dispatch_settings.Application(),
    )
    app.add_host_app('discounts.taxi.yandex.net', discounts.Application())
    app.add_host_app('distlocks.taxi.yandex.net', distlocks.Application())
    app.add_host_app(
        'driver-weariness.taxi.yandex.net', driver_weariness.Application(),
    )
    app.add_host_app(
        'eater-authorizer.eda.yandex.net', eater_authorizer.Application(),
    )
    app.add_host_app('elasticsearch.yandex.net', elasticsearch.Application())
    app.add_host_app(
        'experiments3.taxi.yandex.net', experiments3.Application(),
    )
    app.add_host_app('fleet-rent.taxi.yandex.net', fleet_rent.Application())
    app.add_host_app('trust-paysys.paysys.yandex.net', billing_app)
    app.add_host_app('trust-lpm.paysys.yandex.net', billing_app)
    app.add_host_app('tst.extjams.maps.yandex.net', extjams.Application())
    app.add_host_app('eda.yandex', eda_core_app)
    app.add_host_app('core.eda.yandex.net', eda_core_app)
    app.add_host_app(
        'eats-picker-payment.eda.yandex.net',
        eats_picker_payment.Application(),
    )
    app.add_host_app(
        'eda-delivery-price.eda.yandex.net', eats_delivery_price.Application(),
    )
    app.add_host_app(
        'eats-order-send.eda.yandex.net', eats_order_send.Application(),
    )
    app.add_host_app('geoareas.taxi.yandex.net', geoareas.Application())
    app.add_host_app(
        'special-zones.taxi.yandex.net', special_zones.Application(),
    )
    app.add_host_app(
        'pickuppoints.taxi.yandex.net', pickuppoints.Application(),
    )
    app.add_host_app(
        'logistic-dispatcher.taxi.yandex.net',
        logistic_dispatcher.Application(),
    )
    app.add_host_app('lbs-cloud-proxy.taxi.yandex.net', lbsproxy.Application())
    app.add_host_app(
        'lbs-cloud-proxy.taxi.tst.yandex.net', lbsproxy.Application(),
    )
    app.add_host_app('mock-server.yandex.net', mockserver.Application())
    app.add_host_app('saturn.mlp.yandex.net', saturn.Application())
    app.add_host_app('s3.mds.yandex.net', mds.Application())
    app.add_host_app('s3.mdst.yandex.net', mds.Application())
    app.add_host_app('blackbox.yandex.net', passport_app)
    app.add_host_app('blackbox.yandex-team.ru', passport_app)
    app.add_host_app(
        'passport-internal.yandex.ru', passport_internal.Application(),
    )
    app.add_host_app(
        'payments-eda.taxi.yandex.net', payments_eda.Application(),
    )
    app.add_host_app('personal.taxi.yandex.net', personal.Application())
    app.add_host_app(
        'pricing-data-preparer.taxi.yandex.net',
        pricing_data_preparer.Application(),
    )
    app.add_host_app(
        'core-driving-router.maps.yandex.net', yamaps_router.Application(),
    )
    app.add_host_app(
        'secured-openapi.business.tinkoff.ru', tinkoff_secured.Application(),
    )
    app.add_host_app('suggest-maps.yandex.net', suggest_maps.Application())
    app.add_host_app(
        'mapsuggest-internal.yandex.net', suggest_maps.Application(),
    )
    app.add_host_app('tvm-api.yandex.net', tvm.Application())
    app.add_host_app('login.uber.com', uber_token.Application())
    app.add_host_app('bunker-api.yandex.net', bunker.Application())
    yt_application = yt.Application()
    app.add_host_app('seneca-man.yt.yandex.net', yt_application)
    app.add_host_app('seneca-vla.yt.yandex.net', yt_application)
    app.add_host_app('seneca-sas.yt.yandex.net', yt_application)
    app.add_host_app('statistics.taxi.yandex.net', statistics.Application())
    app.add_host_app(
        'superapp-misc.taxi.yandex.net', superapp_misc.Application(),
    )
    app.add_host_app(
        'superapp-misc.taxi.tst.yandex.net', superapp_misc.Application(),
    )
    app.add_host_app(
        'transactions-eda.taxi.yandex.net', transactions_eda.Application(),
    )
    app.add_host_app('user-api.taxi.yandex.net', user_api.Application())
    app.add_host_app('replication.taxi.yandex.net', replication.Application())
    app.add_host_app('user-state.taxi.yandex.net', user_state.Application())
    app.add_host_app('c.yandex-team.ru', conductor.Application())
    app.add_host_app(
        'quality-control.taxi.yandex.net', quality_control.Application(),
    )
    app.add_host_app('blocklist.taxi.yandex.net', blocklist.Application())
    app.add_host_app(
        'quality-control-cpp.taxi.yandex.net',
        quality_control_cpp.Application(),
    )
    app.add_host_app(
        'eda-surge-calculator.eda.yandex.net',
        eda_surge_calculator.Application(),
    )
    app.add_host_app(
        'surge-calculator.taxi.yandex.net', surge_calculator.Application(),
    )
    app.add_host_app(
        'driver-profiles.taxi.yandex.net', driver_profiles.Application(),
    )
    app.add_host_app(
        'admin-pipeline.taxi.yandex.net', admin_pipeline.Application(),
    )
    app.add_host_app(
        'grocery-checkins.lavka.yandex.net', grocery_checkins.Application(),
    )
    app.add_host_app(
        'grocery-depots.lavka.yandex.net', grocery_depots.Application(),
    )
    app.add_host_app(
        'grocery_surge.lavka.yandex.net', grocery_surge.Application(),
    )
    app.add_host_app(
        'selfemployed-fns-replica.taxi.yandex.net',
        selfemployed_fns_replica.Application(),
    )
    app.add_host_app(
        'stable.leasing-cabinet.carsharing.yandex.net',
        ext_drivematics.Application(),
    )
    app.add_host_app(
        'eda-candidates.taxi.yandex.net', eda_candidates.Application(),
    )
    app.add_host_app('eats-tags.eda.yandex.net', eats_tags.Application())
    app.add_host_app('eats-plus.eda.yandex.net', eats_plus.Application())
    app.add_host_app('umlaas-eats.taxi.yandex.net', umlaas_eats.Application())
    app.add_host_app('eats-eta.eda.yandex.net', eats_eta.Application())
    app.add_host_app(
        'contractor-order-history.taxi.yandex.net',
        contractor_order_history.Application(),
    )
    app.add_host_app(
        'pricing-taximeter.taxi.yandex.net', pricing_taximeter.Application(),
    )
    app.add_host_app(
        'eats-order-stats.eda.yandex.net', eats_order_stats.Application(),
    )
    app.add_host_app(
        'eats-payment-methods-availability.eda.yandex.net',
        eats_payment_methods_availability.Application(),
    )
    app.add_host_app(
        'eats-products.eda.yandex.net', eats_products.Application(),
    )
    app.add_host_app(
        'eats-smart-prices.eda.yandex.net', eats_smart_prices.Application(),
    )
    app.add_host_app('processing.taxi.yandex.net', processing.Application())
    app.add_host_app(
        'driver-login.taxi.yandex.net', driver_login.Application(),
    )
    app.add_host_app('taximeter.yandex.rostaxi.org', taximeter.Application())
    app.add_host_app('yagr.taxi.yandex.net', yagr.Application())
    app.add_host_app(
        'checkprovider.edadeal.yandex.net',
        checkprovider_edadeal.Application(),
    )
    app.add_host_app(
        'grocery-checkins.taxi.yandex.net', grocery_checkins.Application(),
    )
    app.add_host_app('cargo-corp.taxi.yandex.net', cargo_corp.Application())
    app.add_host_app(
        'individual-tariffs.taxi.yandex.net', individual_tariffs.Application(),
    )
    if hasattr(app, 'freeze'):
        app.freeze()
    return app
