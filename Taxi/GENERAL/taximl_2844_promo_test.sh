# https://st.yandex-team.ru/TAXIML-2844
# 5 groups with item promo

python -m projects.lavka.suggest.experiments.calculate \
  --path-yt-working-dir //home/taxi_ml/dev/lavka_upsale/experiments/taximl_2844_promo_new/{} \
  --date-from 2020-08-18 \
  --date-to 2020-08-31 \
  --position-control 1 \
  --positions-test 2 3 4 5 \
  --experiment-name grocery_suggest_ml_promo
