from view import MarkupViewCreator

from collections import defaultdict

import os
import random
import math

POSITIVE_CLASS = 1
NEGATIVE_CLASS = 0


class Hypo(object):
    def __init__(self, text_id, object_id, begin, end, target_class, predicted_class, score):
        assert(type(target_class) is bool)
        assert(type(predicted_class) is bool)
        assert(type(text_id) is int)

        self.text_id = text_id
        self.object_id = object_id

        self.begin = begin
        self.end = end

        self.target_class = target_class
        self.predicted_class = predicted_class

        self.score = score

    def is_true_positive(self):
        return self.predicted_class and self.target_class

    def is_false_positive(self):
        return self.predicted_class and not self.target_class

    def is_false_negative(self):
        return not self.predicted_class and self.target_class

    def is_error_predict(self):
        return self.is_false_positive() or self.is_false_negative()

    @staticmethod
    def from_mtrxn_output_line(line, markup_threshold=0.5, prediction_threshold=0.0):
        parts = line.strip().split('\t', 5)
        target_class = int(parts[1]) > markup_threshold
        label = parts[2]
        score = float(parts[4])
        predicted_class = score > prediction_threshold

        label_fields = label.split('-')
        text_id, object_id = int(label_fields[0]), label_fields[-1]

        # Hypos in significance pool are without positions
        begin, length = 0, 0
        if len(label_fields) == 5:
            begin = int(label_fields[2])
            length = int(label_fields[3])

        return Hypo(text_id, object_id, begin, begin + length, target_class, predicted_class, score)


def calc_precision(hypos):
    true_positives = [h for h in hypos if h.is_true_positive()]
    predicted_positives = [h for h in hypos if h.predicted_class]

    return float(len(true_positives)) / len(predicted_positives) if predicted_positives else 0.0


def calc_recall(hypos):
    true_positives = [h for h in hypos if h.is_true_positive()]
    target_positives = [h for h in hypos if h.target_class]

    return float(len(true_positives)) / len(target_positives) if target_positives else 0.0


# Unused (remove in in next commit)
'''
def create_pool(ideal_markup, features, pool):
    markup = {}
    with open(ideal_markup, "r") as f:
        for line in f.readlines():
            parts = line.strip().split("\t")
            key = "-".join(parts[:4])
            markup[key] = "0"
            if parts[-1] == "t":
                markup[key] = "1"

    index = 0
    with open(pool, "w") as p:
        with open(features, "r") as f:
            for line in f.readlines():
                parts = line.strip().split("\t")
                key = "-".join(parts[:4])
                if key in markup:
                    row = [str(index), markup[key], key, '0'] + parts[4:]
                    p.write("\t".join(row) + "\n")
                    index += 1
'''


def get_test_split_id(number_of_splits, rnd):
    step = 1.0 / number_of_splits
    start = 0.0
    for i in xrange(number_of_splits):
        if start <= rnd and start + step > rnd:
            return i
        start += step
    return number_of_splits - 1


def split_pool(pool, number_of_splits, dest_dir, prefix=''):
    records_by_doc = defaultdict(list)
    with open(pool, "r") as f:
        for line in f.readlines():
            hypo = Hypo.from_mtrxn_output_line(line)
            records_by_doc[hypo.text_id].append(line.strip())

    output_files = []

    for i in xrange(0, number_of_splits):
        output_dir = os.path.join(dest_dir, "split%d" % i)
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)

        learn_file = open(os.path.join(output_dir, prefix + "learn.tsv"), "w")
        test_file = open(os.path.join(output_dir, prefix + "test.tsv"), "w")
        output_files.append((learn_file, test_file))

    # Use fixed seed to always get identical splits
    random.seed(123456789)

    for records in records_by_doc.values():
        rnd = random.random()

        test_id = get_test_split_id(number_of_splits, rnd)

        for i in xrange(number_of_splits):
            if i != test_id:
                output_files[i][0].write("\n".join(records) + "\n")
            else:
                output_files[i][1].write("\n".join(records) + "\n")

    for learn_file, test_file in output_files:
        learn_file.close()
        test_file.close()


# All hypos with positive score but intersected with hypos with more scores considered as false predicted hypos
# (Rule: not more than one true hypos on text charter)
def remove_intersected_true_predicts(hypos):
    hypos.sort(key=lambda h: (h.begin, h.end, h.score))
    for cur_index in xrange(len(hypos)):
        if not hypos[cur_index].predicted_class:
            continue
        for other_index in xrange(cur_index + 1, len(hypos)):
            if hypos[other_index].begin >= hypos[cur_index].end:
                break

            if hypos[other_index].score > hypos[cur_index].score:
                hypos[cur_index].predicted_class = False

    hypos.sort(key=lambda h: (h.end, h.begin, -h.score), reverse=True)
    for cur_index in xrange(len(hypos)):
        if not hypos[cur_index].predicted_class:
            continue
        for other_index in xrange(cur_index + 1, len(hypos)):
            if hypos[other_index].end <= hypos[cur_index].begin:
                break

            if hypos[other_index].score > hypos[cur_index].score:
                hypos[cur_index].predicted_class = False


def split_quality(prediction_threshold, split_file_name, filter_file_name, markup_threshold=0.5):
    unfiltered_total_pos = 0
    if os.path.isfile(filter_file_name):
        with open(filter_file_name, 'r') as f:
            for line in f.readlines():
                hypo = Hypo.from_mtrxn_output_line(line, markup_threshold, prediction_threshold)
                if hypo.target_class:
                    unfiltered_total_pos += 1

    doc_results = {}
    with open(split_file_name, "r") as f:
        for line in f.readlines():
            hypo = Hypo.from_mtrxn_output_line(line, markup_threshold, prediction_threshold)
            if hypo.text_id not in doc_results:
                doc_results[hypo.text_id] = []

            doc_results[hypo.text_id].append(hypo)

    for hypos in doc_results.values():
        remove_intersected_true_predicts(hypos)

    flatten_hypos = [h for hypos in doc_results.values() for h in hypos]
    precision = calc_precision(flatten_hypos)
    recall = calc_recall(flatten_hypos)
    fmeasure = 2.0 * precision * recall / (precision + recall)

    get_errors = lambda hypos: [h for h in hypos if h.is_error_predict()]
    markup_errors = dict([(text_id, get_errors(hypos)) for (text_id, hypos) in doc_results.items() if get_errors(hypos)])

    return (precision, recall, fmeasure, markup_errors)


def mean(x):
    return sum(x) / float(len(x))


def variance(x):
    assert len(x) >= 2
    m = mean(x)
    return sum([(t - m) ** 2 for t in x]) / float(len(x) - 1)


def mean_standard_error(x):
    return math.sqrt(variance(x) / float(len(x)))


def t_critical_095(df):
    df = int(df)
    assert df >= 1
    tbl = {
        1: 12.706,
        2: 4.302,
        3: 3.182,
        4: 2.776,
        5: 2.570,
        6: 2.446,
        7: 2.364,
        8: 2.306,
        9: 2.262,
        10: 2.228,
    }
    if df in tbl:
        return tbl[df]
    else:
        return tbl[max(tbl.keys())]


def conf_int_095(x):
    return mean_standard_error(x) * t_critical_095(len(x) - 1)


def calc_splits_qualities(predict_threshold, dst_path, texts_path, markup_errors_output_file, **params):
    markup_threshold = params.get('markup_threshold', 0.5)
    prefix = params.get('prefix', '')

    precisions = []
    recalls = []
    fmeasures = []
    markup_errors_all = defaultdict(list)
    for d in os.listdir(dst_path):
        split_file = os.path.join(dst_path, d, prefix + "test.tsv.test.matrixnet")
        split_filter_file = os.path.join(dst_path, d, prefix + 'filter_test.tsv')
        curr_precision, curr_recall, curr_fmeasure, markup_errors =\
            split_quality(predict_threshold, split_file, split_filter_file, markup_threshold)
        precisions.append(curr_precision)
        recalls.append(curr_recall)
        fmeasures.append(curr_fmeasure)
        markup_errors_all.update(markup_errors)

    with open(markup_errors_output_file, 'w') as output:
        markup_creator = MarkupViewCreator()
        markup_creator.create(markup_errors_all, texts_path, output)

    return (precisions, recalls, fmeasures)


def quality(precisions, recalls, fmeasures):
    precision_interval = 0
    recall_interval = 0
    fm_interval = 0
    if len(precisions) >= 2:
        # estimates for confidence intervals are valid only under this condition
        precision_interval = conf_int_095(precisions)
        recall_interval = conf_int_095(recalls)
        fm_interval = conf_int_095(fmeasures)
    return (mean(precisions), mean(recalls), mean(fmeasures), precision_interval, recall_interval, fm_interval)

# print calc_splits_qualities(0.0, 'tests', 'texts.tsv', 'res.xls')
