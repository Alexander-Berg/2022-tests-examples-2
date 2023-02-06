# -*- coding: utf-8 -*-

import pytest

from taxi.core import db
from taxi.internal import dbh
from taxi.internal import mph
from taxi.internal.subvention_kit import calculation_context
from taxi.internal.subvention_kit import subvention_handler

from taxi.util import decimal


@pytest.mark.filldb()
@pytest.inline_callbacks
def test_get_all_subventions_with_matched_rules():
    mph_thresholds = mph.Cache()
    yield mph_thresholds.load()
    tariff_settings = yield dbh.tariff_settings.Doc.find_many(
        {}, fields=[
            dbh.tariff_settings.Doc.tz, dbh.tariff_settings.Doc.home_zone
        ]
    )
    tariff_settings = {
        doc.home_zone: doc for doc in tariff_settings
    }

    order_docs = yield db.orders.find().run()
    order_docs = map(dbh.orders.Doc, order_docs)
    mph_values, order_docs, _ = yield mph.bulk_check_thresholds(
        order_docs, mph_thresholds, tariff_settings
    )
    for order_doc in order_docs:
        order = dbh.orders.Doc(order_doc)
        context = calculation_context.CalculationContext(
            {order.pk: decimal.Decimal(100)}, mph_values
        )
        yield subvention_handler.get_all_subventions_with_matched_rules(
            order=order,
            context=context,
        )
