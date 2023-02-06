import logging
from datetime import datetime
from decimal import Decimal
from sandbox.projects.mobile_apps.hypercube_statistic import Calculate


logger = logging.getLogger("test_logger")


def test_general_rate():
    '''
        Test purpose:  check general rate for DDV method
    '''
    logger.info("Calculate general rates")
    test_obj = Calculate()
    assert test_obj.rate == {0: 0.5, 1: 0.25, 2: 0.125, 3: 0.125}


def test_rate_for_date():
    '''
    Test purpose:  check rate
    '''
    logger.info("Calculate rate")
    purchase_date = datetime(2020, 1, 1)
    test_obj = Calculate()
    assert test_obj.get_rate(purchase_date, datetime(2019, 1, 10)) == 0.0
    assert test_obj.get_rate(purchase_date, datetime(2020, 1, 10)) == 0.5
    assert test_obj.get_rate(purchase_date, datetime(2021, 1, 10)) == 0.25
    assert test_obj.get_rate(purchase_date, datetime(2022, 1, 10)) == 0.125
    assert test_obj.get_rate(purchase_date, datetime(2023, 1, 10)) == 0.125
    assert test_obj.get_rate(purchase_date, datetime(2024, 1, 10)) == 0.0


def test_period_cost():
    _TWOPLACES = Decimal(10) ** -2
    events_8BMY118KQ = [
        (1562558827, "dolnikov", "tesseract"),
        (1562584741, "sergets", "reserved"),
        (1562584994, "sergets", "operator"),
        (1562610273, "sergets", "tesseract"),
        (1562610456, "prokopenkova", "operator"),
        (1562611761, "prokopenkova", "tesseract"),
        (1562676078, "novikaud", "operator"),
        (1562693561, "novikaud", "tesseract"),
        (1562759840, "novikaud", "operator"),
        (1562761375, "novikaud", "tesseract"),
        (1562767688, "prokopenkova", "operator"),
        (1562950117, "prokopenkova", "tesseract")
    ]

    events_42000e26d2791300 = [
        (1562606168, "qedastrials", "giveAway"),
        (1562606168, "ezoteva", "takeAway"),
        (1562920618, "ezoteva", "tesseract"),
        (1562920682, "ezoteva", "operator"),
        (1562920683, "ezoteva", "tesseract")
    ]
    test_obj = Calculate()

    # calculate rental events for r2d2, as initial owner
    period_start = (datetime(2019, 7, 8) - datetime(1970, 1, 1)).total_seconds()
    period_end = (datetime(2019, 7, 13) - datetime(1970, 1, 1)).total_seconds()
    purchase_date = datetime(2019, 1, 10)
    logger.info(purchase_date)
    result = test_obj.period_cost(initial_owner='r2d2',
                                  device_events=events_8BMY118KQ,
                                  period_start=period_start,
                                  period_end=period_end,
                                  purchase_date=purchase_date.date(),
                                  purchase_price=10000
                                  )
    logger.info(result)
    # Check that final owner is tesseract and user count is 5 for this device
    assert result[1] == 'tesseract'
    assert len(result[0]) == 5
    assert result[0]['r2d2'] == Decimal(2.35).quantize(_TWOPLACES)
    assert result[0]['prokopenkova'] == Decimal(29.13).quantize(_TWOPLACES)
    assert result[0]['sergets'] == Decimal(4.01).quantize(_TWOPLACES)
    assert result[0]['novikaud'] == Decimal(3.01).quantize(_TWOPLACES)
    assert result[0]['tesseract'] == Decimal(29.99).quantize(_TWOPLACES)

    # How it was calculated:
    # r2d2: (float(1562558827 - (1562533200 + 3*3600) ) / 60) * 10000 * 0.5 / (365 * 24 * 60) = 2,3508054287
    # +3*3600 - MOW timezone
    # prokopenkova: (float(1562950117 - 1562767688 + 1562611761 - 1562610456) / 60) * 10000 * 0.5 / (365 * 24 * 60) = 29.130834601725013
    # sergets: (float(1562610273 - 1562584994) / 60) * 10000 * 0.5 / (365 * 24 * 60) = 4.007959157787925
    # novikaud: (float(1562761375 - 1562759840  + 1562693561 - 1562676078) / 60) * 10000 * 0.5 / (365 * 24 * 60) = 3.015284119736174

    # test that rental cost is twice less for a second year, bc purchase_date is 2018
    period_start = (datetime(2019, 7, 8) - datetime(1970, 1, 1)).total_seconds()
    period_end = (datetime(2019, 7, 13) - datetime(1970, 1, 1)).total_seconds()
    purchase_date = datetime(2018, 1, 10)
    result = test_obj.period_cost(initial_owner='r2d2',
                                  device_events=events_8BMY118KQ,
                                  period_start=period_start,
                                  period_end=period_end,
                                  purchase_date=purchase_date.date(),
                                  purchase_price=10000
                                  )

    logger.info(result)
    assert result[1] == 'tesseract'
    assert len(result[0]) == 5
    assert result[0]['prokopenkova'] == Decimal(14.56).quantize(_TWOPLACES)
    assert result[0]['sergets'] == Decimal(2).quantize(_TWOPLACES)

    # test rental cost is zero, since device was bought more than a 4 uears ago
    period_start = (datetime(2019, 7, 8) - datetime(1970, 1, 1)).total_seconds()
    period_end = (datetime(2019, 7, 13) - datetime(1970, 1, 1)).total_seconds()
    purchase_date = datetime(2014, 1, 10)
    result = test_obj.period_cost(initial_owner='r2d2',
                                  device_events=events_42000e26d2791300,
                                  period_start=period_start,
                                  period_end=period_end,
                                  purchase_date=purchase_date.date(),
                                  purchase_price=10000
                                  )
    logger.info(result)
    assert result[1] == 'tesseract'
    assert len(result[0]) == 0

    # test proper handle of takeAway event
    period_start = (datetime(2019, 7, 8) - datetime(1970, 1, 1)).total_seconds()
    period_end = (datetime(2019, 7, 13) - datetime(1970, 1, 1)).total_seconds()
    purchase_date = datetime(2019, 1, 10)
    result = test_obj.period_cost(initial_owner='r2d2',
                                  device_events=events_42000e26d2791300,
                                  period_start=period_start,
                                  period_end=period_end,
                                  purchase_date=purchase_date.date(),
                                  purchase_price=10000
                                  )
    logger.info(result)
    assert result[0]['ezoteva'] == Decimal(49.86).quantize(_TWOPLACES)
    # ezoteva (float(1562920618 - 1562606168 + 1562920683 - 1562920682) / 60 * 10000 * 0.5 / (365 * 24 * 60) = 49.85587899543379
