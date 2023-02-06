# -*- coding: utf-8 -*-

import argparse

import matplotlib.pyplot as plt
import numpy as np
import yt.wrapper as yt
from catboost import CatBoostRegressor
from sklearn.feature_extraction import DictVectorizer
from sklearn.pipeline import make_pipeline
from tqdm import tqdm
from zoo.optimal_offer.optimal_offer_model.optimal_offer_model import OptimalOffer
from zoo.utils.uplift.evaluation import efficiency_curve_multitreatment
from zoo.optimal_offer.run_driver_offers.utils import hash_function


DEFAULT_SEED = 42
DEFAULT_THRESHOLD = 0.155
ACTIONS_MAPPING = {'control': 0, 'add': 1, 'shift': 2}
ACTIONS = ['control', 'add', 'shift']

FEATURES_LST = [
    'distance_sum_14',
    'distance_sum_7',
    'distance_verybusy_sum_14',
    'distance_verybusy_sum_7',
    'duration_sec_sum_14',
    'duration_sec_sum_7',
    'duration_sec_verybusy_sum_14',
    'duration_sec_verybusy_sum_7',
    'worked_days_14',
    'worked_days_7'
]

FEATURES_ORDERS_LST = [
    'n_orders_14',
    'n_orders_7'
]

FEATURES_COST_LST = [
    'order_cost_14',
    'order_cost_7'
]


def create_features(data):
    X = []
    for row in data:
        x = {l: (row[l] or 0) for l in FEATURES_LST}
        x.update({l: (row[l] or 0) * 1.0 / row['n_orders_city'] for l in
                  FEATURES_ORDERS_LST})
        x.update({l: (row[l] or 0) / row['order_cost_city'] for l in
                  FEATURES_COST_LST})
        X.append(x)

    return X


def extract_t(data):
    t = np.array(
        [ACTIONS_MAPPING[row['group']] for row in data]
    )

    return t


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--threshold', type=float, required=False,
                        default=DEFAULT_THRESHOLD,
                        help='threshold for the model.')

    parser.add_argument('--seed_value', type=int, required=False,
                        default=DEFAULT_SEED,
                        help='The seed value will affect the validation picture')

    parser.add_argument('--salt', type=str, required=True,
                        help='Salt for randomization')

    parser.add_argument('--share_control', type=float, required=True,
                        help='Share of the fully control group')

    parser.add_argument('--share_50_50', type=float, required=True,
                        help='Share of the 50-50 group')

    parser.add_argument('--share_of_targets', type=float,
                        required=False, default=0.5,
                        help='Share of targets in the random assignment group')

    parser.add_argument('--date', type=str,
                        required=True,
                        help='model date')

    args = parser.parse_args()
    np.random.seed(args.seed_value)

    client = yt.YtClient("hahn")
    data = list(
        tqdm(
            client.read_table(
                '//home/taxi_ml/dev/driver_target/data_for_optimal_offer'
            )
        )
    )

    data_apply = list(
        tqdm(
            client.read_table(
                '//home/taxi_ml/dev/driver_target/all_experiments/'
                '{date}/{date}_metrics_filter_joined'.format(date=args.date)
            )
        )
    )

    data_train = [d for d in data if
                  (d['start_date'] == '2019-11-07 00:00:00') | (
                              d['start_date'] == '2019-03-11 00:00:00')]
    data_test = [d for d in data if d['start_date'] > '2020-03-11 00:00:00']


    X = create_features(data_train)
    y = np.array(
        [
            [
                row['target_commission_unr'] +
                (row['group'] == 'add') * (row['target_n_orders_7'] > row['orders_kpi']) * row['bonus_sum'],
                row['target_n_orders_7']
            ]
            for row in data_train
        ]
    )
    t = extract_t(data_train)

    X_test = create_features(data_test)
    y_test = np.array(
        [
            [
                row['target_commission_unr'] +
                (row['group'] == 'add') * (
                            row['target_n_orders_7'] > row['orders_kpi']) * row[
                    'bonus_sum'],
                row['target_n_orders_7']
            ]
            for row in data_test
        ]
    )
    t_test = extract_t(data_test)
    share_test = np.array([[0, 1, 2]]) == t_test[:, np.newaxis]

    effect_shifts = np.mean(y_test[t_test == 2], axis=0) - np.mean(
        y_test[t_test == 0], axis=0)
    effect_aims = np.mean(y_test[t_test == 1], axis=0) - np.mean(
        y_test[t_test == 0], axis=0)

    model = make_pipeline(
        DictVectorizer(sparse=False),
        OptimalOffer(
            CatBoostRegressor(
                loss_function="MultiRMSE",
                iterations=15, max_depth=1
            )
        )
    )

    model.fit(X, y, optimaloffer__t=t)
    prd = model.predict(X_test)
    order = np.random.permutation(len(y_test))
    cum, th = efficiency_curve_multitreatment(y_test[order], t_test[order], -prd[order])
    cum_share, th = efficiency_curve_multitreatment(share_test, t_test, -prd)

    fig = plt.figure(figsize=(16, 8))
    ax1 = fig.add_subplot(111)
    ax1.plot([0, effect_aims[0]], [0, effect_aims[1]], linestyle='--', color='r')
    ax1.plot([0, effect_shifts[0]], [0, effect_shifts[1]], linestyle='--',
             color='g')
    ax1.plot(cum[:, 0], cum[:, 1])
    ax1.set_xlabel(u'Траты в деньгах на водиеля')
    ax1.set_ylabel(u'Доп поездок')

    plt.savefig('validation_opt_offer.png')

    fig = plt.figure(figsize=(16, 8))
    ax1 = fig.add_subplot(111)
    ax1.plot([0, effect_aims[0] * 10810], [0, effect_aims[1] * 10810],
             linestyle='--', color='r')
    ax1.plot([0, effect_shifts[0] * 10810], [0, effect_shifts[1] * 10810],
             linestyle='--',
             color='g')
    ax1.plot(cum[:, 0] * 10810, cum[:, 1] * 10810)
    ax1.set_xlabel(u'Траты в деньгах итого')
    ax1.set_ylabel(u'Доп поездок')

    plt.savefig('validation_opt_offer_per_city.png')

    fig = plt.figure(figsize=(16, 8))
    ax1 = fig.add_subplot(111)
    ax2 = ax1.twiny()
    share1, = ax1.plot(-cum_share[:, 0], cum_share[:, 1], 'r')
    share2, = ax1.plot(-cum_share[:, 0], cum_share[:, 2], 'b')
    share1.set_label(u'Цели')
    share2.set_label(u'Смены')
    ax1.set_xlabel(u'Траты в деньгах на водиеля')
    ax1.set_ylabel(u'Доп поездок')

    ax1.legend()

    plt.savefig('inspect_opt_offer.png')

    # APPLYING MODEL

    ALL_TABLE = yt.TablePath(
        '//home/taxi_ml/dev/driver_target/all_experiments/'
        '{date}/{date}'.format(date=args.date),
        append=False
    )
    ADD_TABLE = yt.TablePath(
        '//home/taxi_ml/dev/driver_target/all_experiments'
        '/{date}/{date}_add'.format(date=args.date),
        append=False
    )
    SHIFT_TABLE = yt.TablePath(
        '//home/taxi_ml/dev/driver_target/all_experiments/'
        '{date}/{date}_shift'.format(date=args.date),
        append=False
    )
    CONTROL_GROUP_TABLE = yt.TablePath(
        '//home/taxi_ml/dev/driver_target/all_experiments/'
        '{date}/{date}_control'.format(date=args.date),
        append=False
    )
    MODEL_GROUP_TABLE = yt.TablePath(
        '//home/taxi_ml/dev/driver_target/all_experiments'
        '/{date}/{date}_model'.format(date=args.date),
        append=False
    )
    _50_50_GROUP_TABLE = yt.TablePath(
        '//home/taxi_ml/dev/driver_target/all_experiments/'
        '{date}/{date}_50_50'.format(date=args.date),
        append=False
    )

    CONFIG_TABLE = yt.TablePath(
        '//home/taxi_ml/dev/drivers/experiments_configs/experiment_{}'.format(
            args.date
        ),
        append=True
    )

    config = {
        "experiment_name": "experiment_{date}".format(date=args.date),
        "groups": [
            [
                str(MODEL_GROUP_TABLE),
                str(CONTROL_GROUP_TABLE)
            ],
            [
                str(MODEL_GROUP_TABLE),
                str(_50_50_GROUP_TABLE)
            ],
            [
                str(_50_50_GROUP_TABLE),
                str(CONTROL_GROUP_TABLE)

            ]
        ],
        "groups_names":[
            [
                "model",
                "control"
            ],
            [
                "model",
                "50-50"
            ],
            [
                "50-50",
                "control"
            ]
        ],
        "periods_list": [

        ]
    }

    data_apply = filter(lambda x: x['worked_days_21'] >= 2, data_apply)
    X_apply = create_features(data_apply)
    predictions = model.predict(X_apply)
    actions = model.steps[-1][1].get_action_from_predictions(
        predictions, threshold=args.threshold
    )

    output = []
    for row, pred, action in zip(data_apply, predictions, actions):
        new_row = {
            'unique_driver_id': row['unique_driver_id'],
            'control_score': pred[0],
            'tariff_zone': row['tariff_zone'],
            'prediction_date': row['datetime_exp'],
            'add_score': pred[1],
            'shift_score': pred[2],
            'action_model': ACTIONS[action],
            'hash_for_rnd': (
                hash_function(
                    row['unique_driver_id'] + args.salt
                ) % 2.0 ** 16 / 2.0 ** 16
            ),
            'hash_for_50_50': (
                hash_function(
                    row['unique_driver_id'] +
                    hash_function(args.salt + '_for_50_50')
                ) % 2.0 ** 16 / 2.0 ** 16
            ),
        }

        if new_row['hash_for_rnd'] < args.share_control:
            new_row['group'] = 'control'
        elif new_row['hash_for_rnd'] < args.share_control + args.share_50_50:
            new_row['group'] = '50_50'
        else:
            new_row['group'] = 'model'

        if new_row['hash_for_50_50'] < args.share_of_targets:
            new_row['action_50_50'] = 'add'
        else:
            new_row['action_50_50'] = 'shift'

        output.append(new_row)


    client.write_table(ALL_TABLE, output, raw=False)
    client.write_table(
        SHIFT_TABLE,
        filter(
            lambda row:
            (row['group'] == 'model' and row['action_model'] == 'shift') or
            (row['group'] == '50_50' and row['action_50_50'] == 'shift'),
            output
        ),
        raw=False
    )
    client.write_table(
        ADD_TABLE,
        filter(
            lambda row:
            (row['group'] == 'model' and row['action_model'] == 'add') or
            (row['group'] == '50_50' and row['action_50_50'] == 'add'),
            output
        ),
        raw=False
    )

    client.write_table(
        CONTROL_GROUP_TABLE,
        filter(
            lambda row:
            (row['group'] == 'control'),
            output
        ),
        raw=False
    )

    client.write_table(
        MODEL_GROUP_TABLE,
        filter(
            lambda row:
            (row['group'] == 'model'),
            output
        ),
        raw=False
    )

    client.write_table(
        _50_50_GROUP_TABLE,
        filter(
            lambda row:
            (row['group'] == '50_50'),
            output
        ),
        raw=False
    )

    client.write_table(
        CONFIG_TABLE,
        [{'config': config}],
        raw=False
    )
