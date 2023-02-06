package ru.yandex.autotests.metrika.sort;

import org.apache.commons.lang3.StringUtils;
import org.apache.commons.lang3.tuple.MutablePair;
import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.metrika.data.parameters.report.v1.CommonReportParameters;
import org.apache.http.NameValuePair;

import java.util.Deque;
import java.util.LinkedList;
import java.util.List;

import static ch.lambdaj.Lambda.on;
import static ch.lambdaj.collection.LambdaCollections.with;

/**
 * Created by konkov on 25.12.2014.
 *
 * построение выражений сортировки
 */
public class SortBuilder implements IFormParameters {

    public static final String DESCENDING = "-";
    private static final String SEPARATOR = ",";

    private Deque<MutablePair<String, String>> terms = new LinkedList<>();

    public String build() {
        return with(terms.descendingIterator()).extract(on(MutablePair.class).toString("%s%s")).join(SEPARATOR);
    }

    public static SortBuilder sort() {
        return new SortBuilder();
    }

    public SortBuilder by(String metricOrDimension) {
        terms.push(MutablePair.of(StringUtils.EMPTY, metricOrDimension));
        return this;
    }

    public SortBuilder descending() {
        terms.peek().setLeft(DESCENDING);
        return this;
    }

    @Override
    public List<NameValuePair> getParameters() {
        return new CommonReportParameters().withSort(this.build()).getParameters();
    }
}
