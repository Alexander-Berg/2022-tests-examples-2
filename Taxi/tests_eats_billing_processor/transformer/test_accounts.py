import pytest
import yaml


from tests_eats_billing_processor.transformer import helper


SIMPLE_ACCOUNTING = yaml.load(
    """
default:
    order_gmv:
      - account:
          - name: gmv
          - order_nr#xget: /event/order_nr
          - client_id#xget: /event/place_id
          - transaction_date#xget: /event/transaction_date
          - amount#xget: /event/gmv_amount
""",
    Loader=yaml.SafeLoader,
)


DOUBLE_ACCOUNTING = yaml.load(
    """
default:
    order_gmv:
      - account:
          - name: gmv
          - order_nr#xget: /event/order_nr
          - client_id#xget: /event/place_id
          - transaction_date#xget: /event/transaction_date
          - amount#mul:
                values#array:
                  - value#xget: /event/gmv_amount
                  - value: '2'
""",
    Loader=yaml.SafeLoader,
)


ACCUMULATING_ACCOUNTING = yaml.load(
    """
default:
    order_gmv:
      - account:
          - name: gmv
          - order_nr#xget: /event/order_nr
          - client_id#xget: /event/place_id
          - transaction_date#xget: /event/transaction_date
          - amount#xget: /event/gmv_amount
      - account:
          - name: gmv
          - order_nr#xget: /event/order_nr
          - client_id#xget: /event/place_id
          - transaction_date#xget: /event/transaction_date
          - amount#xget: /event/gmv_amount
      - account:
          - name: gmv
          - order_nr#xget: /event/order_nr
          - client_id#xget: /event/place_id
          - transaction_date#xget: /event/transaction_date
          - amount#xget: /event/gmv_amount
""",
    Loader=yaml.SafeLoader,
)


@pytest.mark.config(EATS_BILLING_PROCESSOR_RULES=SIMPLE_ACCOUNTING)
async def test_update(transformer_fixtures):
    await (
        helper.TransformerTest()
        .on_order_gmv(place_id='1111', gmv_amount='100.00')
        .on_order_gmv(place_id='1111', gmv_amount='200.00')
        .expect_accounting(
            client_id='1111', account_type='gmv', amount='200.00',
        )
        .no_stq_call_expected()
        .run(transformer_fixtures)
    )


@pytest.mark.config(EATS_BILLING_PROCESSOR_RULES=SIMPLE_ACCOUNTING)
async def test_update_zero(transformer_fixtures):
    await (
        helper.TransformerTest()
        .on_order_gmv(place_id='1111', gmv_amount='100.00')
        .on_order_gmv(place_id='1111', gmv_amount='200.00')
        .on_order_gmv(place_id='1111', gmv_amount='0')
        .expect_accounting(client_id='1111', account_type='gmv', amount='0.00')
        .no_stq_call_expected()
        .run(transformer_fixtures)
    )


@pytest.mark.config(
    EATS_BILLING_PROCESSOR_RULES=DOUBLE_ACCOUNTING,
    EATS_BILLING_PROCESSOR_RERUN_RULES=SIMPLE_ACCOUNTING,
)
async def test_rerun_update(transformer_fixtures):
    await (
        helper.TransformerTest()
        .on_order_gmv(place_id='1111', gmv_amount='100.00')
        .expect_accounting(
            client_id='1111', account_type='gmv', amount='200.00',
        )
        .no_stq_call_expected()
        .run(transformer_fixtures)
    )

    await (
        helper.TransformerTest()
        .on_rerun(fix_event_id=1)
        .expect_accounting(
            client_id='1111', account_type='gmv', amount='100.00',
        )
        .no_stq_call_expected()
        .run(transformer_fixtures)
    )


@pytest.mark.config(EATS_BILLING_PROCESSOR_RULES=SIMPLE_ACCOUNTING)
@pytest.mark.pgsql('eats_billing_processor', files=['test_accounts.sql'])
async def test_no_update(transformer_fixtures):
    await (
        helper.TransformerTest()
        .on_order_gmv(place_id='1111', gmv_amount='200.00')
        .expect_accounting(
            client_id='1111', account_type='gmv', amount='100.00',
        )
        .no_stq_call_expected()
        .run(transformer_fixtures)
    )


@pytest.mark.config(EATS_BILLING_PROCESSOR_RULES=ACCUMULATING_ACCOUNTING)
async def test_accumulating(transformer_fixtures):
    await (
        helper.TransformerTest()
        .on_order_gmv(place_id='1111', gmv_amount='200.00')
        .expect_accounting(
            client_id='1111', account_type='gmv', amount='600.00',
        )
        .no_stq_call_expected()
        .run(transformer_fixtures)
    )
