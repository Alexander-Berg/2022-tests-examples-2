from library.python import resource
import vh3
from .main import (
    train_model,
    weather_features,
    calc_yql1,
    orders_with_accident_moment_target,
    prepare_and_publish_result
)
from .operations import (
    yql_2,
    single_option_to_text_output,
)


@vh3.decorator.graph()
def add_features(
    orders: vh3.MRTable,
    mr_output_ttl: vh3.Integer,
    mr_output_features_ttl: vh3.Integer = None,
    yql_param: vh3.MultipleStrings = (),
) -> vh3.MRTable:
    def calc_yql(script_name: str, input1=[orders], **kwargs) -> vh3.MRTable:
        return calc_yql1(
            script_name=script_name,
            input1=input1,
            param=yql_param,
            mr_output_ttl=mr_output_features_ttl,
            **kwargs
        )
    files_hist = vh3.Connections(**{
        "time_window_aggregator.py": single_option_to_text_output(
            resource.find('time_window_aggregator').decode('utf-8')
        )
    })
    navi_alerts = calc_yql1('match_navi_alerts', param=yql_param, mr_output_ttl=mr_output_features_ttl)
    offline_track = calc_yql('find_offline_track')
    freq=calc_yql('frequency_of_edges')
    return yql_2(
        input1=[orders],
        input2=vh3.Connections(
            order=calc_yql('order_features'),
            executor=calc_yql('driver_features'),
            # session=calc_yql('session_features'),
            # work_schedule_hist=calc_yql('work_schedule_histogram'),
            history=calc_yql('history_features', files=files_hist),
            prev_accidents=calc_yql('prev_accidents', files=files_hist),
            telemetry=calc_yql('telemetry_features', files=files_hist),
            weather=weather_features(
                orders=orders,
                yql_param=yql_param,
                mr_output_ttl=mr_output_features_ttl,
            ),
            track_offline=calc_yql(
                'calc_track_features',
                input1=vh3.Connections(
                    orders_edges=offline_track,
                    event_with_edges=navi_alerts,
                )
            ),
            drivers_norm_track_offline=calc_yql(
                'drivers_norm_calc_track_features',
                input1=vh3.Connections(
                    orders_edges=offline_track,
                    event_with_edges=navi_alerts,
                    freq=freq
                )
            ),
            crit_norm_track=calc_yql(
                'crit_points_norm_calc_track_features',
                input1=vh3.Connections(
                    orders_edges=offline_track,
                    freq=freq,
                    crit_count=calc_yql('crit_points_per_edge')
                )
            )
        ),
        request=resource.find("join_features").decode("utf-8"),
        yql_operation_title="YQL Join features",
        mr_output_ttl=mr_output_ttl,
        **vh3.block_args(name='join_features'),
    ).output1


@vh3.decorator.graph()
def safety_dispatch_imitation_sergo251000_test(
    *,
    date_from: vh3.String = "2019-10-01",
    date_to: vh3.String = "2021-11-29",
    date_imitation: vh3.String = '2021-11-30',
    description: vh3.String = "Make prob_prod as penalty",
    mr_output_features_ttl: vh3.Integer = 30,
    mr_output_ttl: vh3.Integer = 30,
    yt_secret_key: vh3.String = vh3.Factory(lambda: vh3.context.yt_secret_key),
) -> None:
    yql_param = (vh3.Expr("date_from=${global.date_from}"), vh3.Expr("date_to=${global.date_to}"))
    yql_param_imit = (vh3.Expr("date_from=${global.date_imitation}"), vh3.Expr("date_to=${global.date_imitation}"))
    orders_for_train = orders_with_accident_moment_target(yql_param, mr_output_ttl)
    train_sample_with_features = add_features(
        orders_for_train,
        yql_param=yql_param,
        mr_output_features_ttl=mr_output_features_ttl,
        mr_output_ttl=mr_output_ttl,
    )
    order_imitation = calc_yql1('orders_for_dispatch_imitation', param=yql_param_imit, mr_output_ttl=mr_output_ttl)
    order_imitation_with_features = add_features(
        order_imitation,
        yql_param=yql_param_imit,
        mr_output_features_ttl=mr_output_features_ttl,
        mr_output_ttl=mr_output_ttl,
    )
    train_model_result = train_model(
        order_imitation_with_features,
        train_sample_with_features,
        notebook_parameters=[
            'mode=nirvana',
            'iterations=1000',
            'target_accident=accident_1h',
            'target_injured=injured_1h',
            'target_prod=injured_1h',
            'date_column=moscow_order_dt',
            'date_bound=2021-06-01',
            'features_executor_pattern=executor.*,history.*,telemetry.*,prev_accidents.*',
            'features_executor_prod_pattern=executor.*,history.*,telemetry.*,prev_accidents.*',
            'features_order_pattern=order.*,weather.*,track_offline.*,drivers_norm_track_offline.*',
            'features_order_prod_pattern=track_offline.*,order.city,drivers_norm_track_offline.*,ßorder.country,order.plan_travel_time_min,order.plan_travel_distance_km',
            vh3.Expr('yt_secret_key=${global.yt_secret_key}'),
        ],
        mr_output_ttl=mr_output_ttl,
    )
    pairs_imitation : vh3.MRTable = yql_2(
        input1=[order_imitation_with_features],
        input2=[train_model_result.imitation_scores],
        request=resource.find("prepair_pairs").decode("utf-8"),
        param=(
            vh3.Expr("date_from=${global.date_imitation}"),
            vh3.Expr("date_to=${global.date_imitation}"),
            'order_features=' + ','.join((
                'order.plan_avg_speed_km_per_hour',
                'order.plan_travel_distance_km',
                'order.plan_travel_time_min',
                'track_offline.accidents_365_per_km_norm_by_year_russia_mln',
            ))
        ),
        yql_operation_title="YQL prepair_pairs",
        mr_output_ttl=7,
        **vh3.block_args(name='prepair_pairs'),
    ).output1
    imitation_result = yql_2(
        input1=[pairs_imitation],
        request=resource.find('imitation').decode('utf-8'),
        files=vh3.Connections(**{
            "imitation.py" : single_option_to_text_output(resource.find('imitation_py').decode('utf-8')),
            "coeff.json": train_model_result.coeff,
        }),
        param=[
            'base_score=score + safety_penalty',
            'metrics=' + ','.join([
                'prob_accident',
                'prob_injured',
                'rt',
                'score',
                'order.plan_travel_distance_km',
                'order.plan_travel_time_min',
            ]),
            'use_normalize_coeff=true',
            'penalty_grid=0,10,20,30,50',
            'penalty_expr=prob_prod',
        ],
        yql_operation_title="YQL imitation",
        **vh3.block_args(name='imitation'),
    )
    prepare_and_publish_result(
        metrics_diff=imitation_result.output1,
        change_pairs_diff=imitation_result.output2,
        accident_models_aucs=train_model_result.accident_models_aucs,
        description=description,
        date_from=date_from,
        date_to=date_to,
        date_imitation=date_imitation,
    )
