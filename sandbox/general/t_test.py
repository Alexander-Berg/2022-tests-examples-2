from __future__ import print_function
import sys
import json
import numpy as np


def load(file_name):
    with open(file_name) as f:
        res = json.load(f)
    return res


def main():
    from scipy import stats as st

    if len(sys.argv) < 3:
        print("Usage: {} <res1.json> <res2.json>".format(sys.argv[0]))
        sys.exit(1)

    sample1 = load(sys.argv[1])
    sample2 = load(sys.argv[2])
    median_rps_1 = np.median(sample1)
    median_rps_2 = np.median(sample2)
    t_stat, p_val = st.mstats.ttest_ind(sample1, sample2, equal_var=False)
    print(json.dumps({
        "t_stat": t_stat,
        "p_value": round(p_val, 4),
        "median_rps_1": median_rps_1,
        "median_rps_2": median_rps_2,
        "diff_per_cent_median": (median_rps_2 - median_rps_1) * 100 / float(median_rps_1),
        "diff_probability": round((1 - p_val) * 100, 2),
    }))


if __name__ == '__main__':
    main()
