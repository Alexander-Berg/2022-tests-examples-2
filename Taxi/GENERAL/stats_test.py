import cyson
import pandas as pd
from itertools import combinations
import numpy as np
from scipy.stats import ttest_rel, wilcoxon, shapiro, probplot
from ast import literal_eval
import json


def safe_float(x):
    try:
        return float(x)
    except:
        pass
    return 0.0


def unstack_df(df, cols_arr):
    df.columns = ["test_group", "bucket_id", "metric_name", "value"]
    df = (
        df.set_index(["test_group", "bucket_id", "metric_name"])
        .unstack(["metric_name"])["value"]
        .rename_axis([None], axis=1)
        .reset_index()
    )

    agg_dict = {{}}
    for c in cols_arr:
        agg_dict[c] = "sum"

    df = df.groupby(["test_group", "bucket_id"]).agg(agg_dict).reset_index()
    for c in cols_arr:
        df[c] = df[c].apply(safe_float)
    return df


def calc_complex_metric(df, metric_dict, analysis_period):
    def _calc_metric(test, control, delta_types):
        delta_1 = (
            test[calc_columns[0]].sum() / test.shape[0]
            - control[calc_columns[0]].sum() / control.shape[0]
        )
        if delta_types[0] == "relative":
            delta_1 = delta_1 / (control[calc_columns[0]].sum() / control.shape[0])

        delta_2 = (
            test[calc_columns[1]].sum() / test.shape[0]
            - control[calc_columns[1]].sum() / control.shape[0]
        )
        if delta_types[1] == "relative":
            delta_2 = delta_2 / (control[calc_columns[1]].sum() / control.shape[0])

        raise ValueError(f'delta 1: {delta_1}, delta 2: {delta_2}')

        if calc_rule == "addition":
            return delta_1 + delta_2
        if calc_rule == "subtraction":
            return delta_1 - delta_2
        if calc_rule == "multiplication":
            return delta_1 * delta_2
        if calc_rule == "division":
            return delta_1 / delta_2
        return np.nan

    def my_bootstrap(df1, df2, delta_types, iters=1000):
        values = []
        size = df1.shape[0]
        for _ in range(1):
            test = df1.sample(n=size, replace=True)
            control = df2.sample(n=size, replace=True)
            values.append(_calc_metric(test, control, delta_types))
        return values

    calc_columns = metric_dict["columns_to_use"]
    calc_rule = metric_dict["additional_action"]
    name = metric_dict["metric_name"]
    delta_types = metric_dict["delta_types"]

    df = unstack_df(df, calc_columns)
    unique_groups = sorted(df["test_group"].unique(), reverse=True)
    has_control = sum(['control' in x for x in unique_groups])>0
    if has_control:
        part_1 = [x for x in unique_groups if 'control' not in x]
        part_2 = [x for x in unique_groups if 'control' in x]
        unique_groups = part_1 + part_2

    results = []
    for first_test_group, second_test_group in combinations(unique_groups, 2):
        test_df = (
            df[df["test_group"] == first_test_group].copy().sort_values("bucket_id").reset_index()
        )
        control_df = (
            df[df["test_group"] == second_test_group].copy().sort_values("bucket_id").reset_index()
        )

        bootstrap_values = my_bootstrap(test_df, control_df, delta_types)
        effect = np.mean(bootstrap_values)
        low = np.percentile(bootstrap_values, 2.5)
        high = np.percentile(bootstrap_values, 97.5)
        shapiro_pvalue = shapiro(bootstrap_values)[1]
        bootstrap_pvalue = (np.array(bootstrap_values) * np.sign(effect) < 0).mean() * 2
        wilcoxon_pvalue, ttest_pvalue = np.nan, np.nan
        lift, low_ci, high_ci = np.nan, np.nan, np.nan

        qqplot, params = probplot(bootstrap_values, dist="norm")
        kkk = [params[0] * x + params[1] for x in qqplot[0]]
        qqplot = list(zip(qqplot[0], qqplot[1], kkk))
        results.append(
            (
                name,
                analysis_period,
                first_test_group,
                second_test_group,
                effect,
                low,
                high,
                lift,
                low_ci,
                high_ci,
                ttest_pvalue,
                wilcoxon_pvalue,
                bootstrap_pvalue,
                shapiro_pvalue,
                qqplot,
            )
        )
    return results


def calc_uplift(df, name, period_of_analysis):
    df.columns = ["test_group", "bucket_id", "value"]
    unique_groups = sorted(df["test_group"].unique(), reverse=True)
    has_control = sum(['control' in x for x in unique_groups])>0
    if has_control:
        part_1 = [x for x in unique_groups if 'control' not in x]
        part_2 = [x for x in unique_groups if 'control' in x]
        unique_groups = part_1 + part_2

    results = []
    for first_test_group, second_test_group in combinations(unique_groups, 2):
        test_array = (
            df[df["test_group"] == first_test_group]
            .copy()
            .sort_values("bucket_id")
            .reset_index()["value"]
            .array
        )
        control_array = (
            df[df["test_group"] == second_test_group]
            .copy()
            .sort_values("bucket_id")
            .reset_index()["value"]
            .array
        )

        effect_array = test_array - control_array
        delta = 1.96 * np.std(effect_array) / np.sqrt(len(effect_array))
        low, high = effect_array.mean() - delta, effect_array.mean() + delta

        wilcoxon_pvalue = wilcoxon(test_array, control_array).pvalue
        ttest_pvalue = ttest_rel(test_array, control_array).pvalue
        shapiro_pvalue = shapiro(effect_array)[1]

        effect = effect_array.mean()
        base_mean = control_array.mean()
        lift = effect_array.mean() / base_mean
        low_ci = low / base_mean
        high_ci = high / base_mean

        qqplot, params = probplot(effect_array, dist="norm")
        kkk = [params[0] * x + params[1] for x in qqplot[0]]
        qqplot = list(zip(qqplot[0], qqplot[1], kkk))
        bootstrap_pvalue = np.nan
        results.append(
            (
                name,
                period_of_analysis,
                first_test_group,
                second_test_group,
                effect,
                low,
                high,
                lift,
                low_ci,
                high_ci,
                ttest_pvalue,
                wilcoxon_pvalue,
                bootstrap_pvalue,
                shapiro_pvalue,
                qqplot,
            )
        )
    return results


def _process_data(data, metric_array, col_names):
    def _filter_additional_columns(metric_array):
        additional_columns = []
        for m in metric_array:
            columns_to_use = m["columns_to_use"]
            if len(columns_to_use) < 2:
                continue
            if "require_delta_for_each_columns" not in m:
                continue
            if m["require_delta_for_each_columns"]:
                continue
            additional_columns.append(m)
        return additional_columns

    def _get_additional_columns(some_df, additional_metric, period_cols):
        calc_cols = additional_metric["columns_to_use"]
        new_metric_name = additional_metric["metric_name"]
        calc_rule = additional_metric["additional_action"]

        to_merge = []
        for x in period_cols:
            sub_df = some_df[["test_group", "bucket_id", "metric_name", x]].copy()
            sub_df = unstack_df(sub_df, calc_cols)

            if calc_rule == "addition":
                sub_df[x] = sub_df[calc_cols[0]] + sub_df[calc_cols[1]]
            if calc_rule == "subtraction":
                sub_df[x] = sub_df[calc_cols[0]] - sub_df[calc_cols[1]]
            if calc_rule == "multiplication":
                sub_df[x] = sub_df[calc_cols[0]] * sub_df[calc_cols[1]]
            if calc_rule == "division":
                sub_df[x] = sub_df[calc_cols[0]] / sub_df[calc_cols[1]]

            sub_df["metric_name"] = new_metric_name
            sub_df = sub_df[["test_group", "bucket_id", "metric_name", x]]
            to_merge.append(sub_df)

        final_df = to_merge[0]
        for m in to_merge[1:]:
            final_df = final_df.merge(m, on=["test_group", "bucket_id", "metric_name"])

        columns = ["test_group", "bucket_id", "metric_name"] + period_cols
        final_df = final_df[columns]
        return final_df

    test_group = []
    bucket_id = []
    metric_name = []
    metric_values = []

    data = cyson.loads(data)
    for i in range(len(data[0][2][0]) - 1):
        metric_values.append([])

    for i in range(len(data)):
        bucket = data[i]
        tg = bucket[0].decode("utf-8")
        b_id = int(bucket[1])
        metrics = bucket[2]

        for j in range(len(metrics)):
            m_name = metrics[j][0].decode("utf-8")
            test_group.append(tg)
            bucket_id.append(b_id)
            metric_name.append(m_name)
            for k in range(1, len(metrics[j])):
                metric_values[k - 1].append(metrics[j][k])

    data_df = pd.DataFrame()
    data_df["test_group"] = test_group
    data_df["bucket_id"] = bucket_id
    data_df["metric_name"] = metric_name
    for i in range(len(col_names)):
        data_df[col_names[i]] = metric_values[i]

    to_concat = [data_df]
    additional_columns = _filter_additional_columns(metric_array)

    for row in additional_columns:
        new_part = _get_additional_columns(data_df, row, col_names)
        to_concat.append(new_part)
        data_df = pd.concat(to_concat)
        to_concat = [data_df]

    return data_df


def parse_markup(data, metric_array, period_analysis):
    def __filter_complex_metrics(metric_array):
        complex_metrics = []
        for m in metric_array:
            columns_to_use = m["columns_to_use"]
            if len(columns_to_use) < 2:
                continue
            if "require_delta_for_each_columns" not in m:
                continue
            if not m["require_delta_for_each_columns"]:
                continue
            complex_metrics.append(m)
        return complex_metrics

    def __filter_basic_metrics(metric_array):
        basic_metrics = []
        for m in metric_array:
            columns_to_use = m["columns_to_use"]
            if len(columns_to_use) < 2:
                if m['metric_type'] == 'user_set':
                    m["columns_to_use"] = [m["metric_name"]]
                basic_metrics.append(m)
            if len(columns_to_use) == 2:
                if not m["require_delta_for_each_columns"]:
                    m["columns_to_use"] = [m["metric_name"]]
                    basic_metrics.append(m)

        return basic_metrics

    metric_array = json.loads(metric_array.decode("utf-8").strip())
    metric_array = metric_array["metrics"]
    period_analysis = [x.strip() for x in literal_eval(period_analysis.decode("utf-8"))]
    data = _process_data(data, metric_array, period_analysis)

    results = []
    basic_metrics = __filter_basic_metrics(metric_array)
    complex_metrics = __filter_complex_metrics(metric_array)

    for row in complex_metrics:
        sub_df = data[data.metric_name.isin(row["columns_to_use"])]
        for t in period_analysis:
            try:
                df_to_use = sub_df[["test_group", "bucket_id", "metric_name", t]].copy()
                results.append(calc_complex_metric(df_to_use, row, t))
                del df_to_use
            except:
                continue

    for row in basic_metrics:
        metric_name = row["metric_name"]
        sub_df = data[data.metric_name.isin(row["columns_to_use"])]
        for t in period_analysis:
            try:
                df_to_use = sub_df[["test_group", "bucket_id", t]]
                results.append(calc_uplift(df_to_use, metric_name, t))
                del df_to_use
            except:
                continue

    flat_list = [x for xs in results for x in xs]
    return flat_list
