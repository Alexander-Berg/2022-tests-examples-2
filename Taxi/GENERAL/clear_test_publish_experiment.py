import asyncio
import logging
import typing

from taxi.clients import taxi_exp
from taxi.maintenance import run

from promotions.generated.cron import cron_context as context_module
from promotions.logic import experiments
from promotions.repositories import storage


logger = logging.getLogger(__name__)


async def clear_test_publish_experiment(
        context: context_module.Context,
        log_extra: typing.Optional[dict] = None,
):
    exp_name = context.config.PROMOTIONS_TEST_PUBLISH_EXP_NAME
    current_exp = await context.client_taxi_exp.get_exp(exp_name)
    storage_base = storage.from_context(context)
    active_promotions = await storage_base.promotions.get_active_by_exp_name(
        exp_name,
    )
    active_promotions.extend(
        await storage_base.promo_on_map.get_active_by_exp_name(exp_name),
    )

    if (
            len(current_exp['clauses']) == 1
            and current_exp['clauses'][0] == experiments.make_default_clause()
    ):
        return

    current_clauses: typing.List[typing.Dict] = []
    for clause in current_exp['clauses']:
        value = clause['value']
        if 'promotions' not in value:
            logger.warning(
                'Clause without \"promotions\" in value was excluded: %s',
                str(clause),
                extra=log_extra,
            )
            continue
        new_promotions = [
            promotion_id
            for promotion_id in value['promotions']
            if promotion_id in active_promotions
        ]
        if not new_promotions:
            logger.info(
                'Clause \"%s\" is empty, excluded',
                clause['title'],
                extra=log_extra,
            )
            continue
        clause['value']['promotions'] = new_promotions
        current_clauses.append(clause)
    if not current_clauses:
        current_clauses.append(experiments.make_default_clause())
    current_exp['clauses'] = current_clauses
    try:
        await context.client_taxi_exp.update_exp(
            exp_name, current_exp['last_modified_at'], current_exp,
        )
    except taxi_exp.RequestError as exc:
        if exc.status == 409:
            logger.warning('Conflict in exp: %s', exc, extra=log_extra)
        else:
            raise exc


async def do_stuff(
        task_context: run.StuffContext,
        loop: asyncio.AbstractEventLoop,
        *,
        log_extra: typing.Optional[dict] = None,
):
    context = typing.cast(context_module.Context, task_context.data)
    logger.info(
        '%s: starting task clearing test publush exp clauses %s',
        context.unit_name,
        task_context.id,
        extra=log_extra,
    )
    await clear_test_publish_experiment(context, log_extra)
    logger.info(
        '%s: ending task clearing test publush exp clauses %s',
        context.unit_name,
        task_context.id,
        extra=log_extra,
    )
