# python -m zoo.optimal_offer.delta_sh_model.train \
#    --start_date 2018-05-10 \
#    --end_date 2019-03-01 \
#    --train_path //home/taxi_ml/dev/driver_target/testing_train \
#    --checkpoints metrics_unique_driver_id

# BEFORE RUNNING:
# export ABK_token="test_token"

(cat <<EOF
{
    "min_working_days" : 2,
    "salt": "test",
    "min_kpi": 25,
    "randomization": [
         {"segment": "add_high", "probability": 0.1, "money_multiplier": 0.4, "bonus_type": "add", "time_intervals": "['{\"end_seconds\": 86400, \"begin_seconds\": 25200}']"},
         {"segment": "add_low", "probability": 0.1, "money_multiplier": 0.3, "bonus_type": "add", "time_intervals": "['{\"end_seconds\": 86400, \"begin_seconds\": 25200}']"},
         {"segment": "flat_high", "probability": 0.1, "flat_bonus_sum": 2000, "bonus_type": "add", "targets_scheme": "flat", "time_intervals": "['{\"end_seconds\": 86400, \"begin_seconds\": 25200}']"},
         {"segment": "flat_default", "probability": 0.1, "bonus_type": "add", "targets_scheme": "flat", "time_intervals": "['{\"end_seconds\": 86400, \"begin_seconds\": 25200}']"},
         {"segment": "shift", "probability": 0.4, "bonus_type": "shift"}
    ]
}
EOF
) > config.json


(cat <<EOF
tariff_zone,share_threshold,expected_budget_threshold
barnaul, 100, 9999999999
irkutsk, 100, 10000
omsk, 10, 999999999999
khabarovsk, 100, 0
EOF
) > cities_config.csv

export ABK_environment="taxi-api-admin.taxi.tst.yandex.net"


python -m zoo.optimal_offer.run_driver_offers.run_driver_offers \
    --dest-folder=//home/taxi_ml/dev/driver_offers/test/some_path \
    --start-date 2020-06-17 \
    --end-date 2020-06-20 \
    --cities-config cities_config.csv \
    --config config.json \
    --flat-bonus-sum=200 \
    --flat-target=60 \
    --money-multiplier=1 \
    --targets-complexity=0.98 \
    --checkpoints metrics \
    --sample active
