package ru.yandex.autotests.metrika.steps.report;

import ru.yandex.autotests.httpclient.lite.core.steps.BackEndBaseSteps;
import ru.yandex.autotests.metrika.data.report.v1.enums.ReportFilterType;
import ru.yandex.autotests.metrika.filters.Expression;
import ru.yandex.autotests.metrika.filters.Term;

import java.util.List;

import static java.util.stream.IntStream.range;
import static ru.yandex.autotests.metrika.filters.Term.empty;

/**
 * Created by sourx on 27.05.2016.
 */
public class AnalyticsFilterSteps extends BackEndBaseSteps {

    private final ReportFilterType REPORT_TYPE = ReportFilterType.ANALYTICS;

    /**
     * Формирует фильтр с одним атрибутом и заданным количеством условий.
     *
     * @param conditionAttribute атрибут для формирования фильтра (метрика, измерение).
     * @param numberOfConditions количество условий в фильтре.
     * @return строка - фильтр.
     */
    public String getAnalyticsFilterWithConditions(String conditionAttribute, int numberOfConditions) {
        return getAnalyticsFilterExpressionWithConditions(conditionAttribute, numberOfConditions).build(REPORT_TYPE);
    }

    public Expression getAnalyticsFilterExpressionWithConditions(String conditionAttribute, int numberOfConditions) {
        return range(0, numberOfConditions)
                .mapToObj(i -> (Expression) Term.term(conditionAttribute).equalTo(i))
                .reduce(empty(), Expression::or);
    }

    /**
     * Формирует фильтр на каждый из переданных атрибутов, но не более указанного количества условий.
     *
     * @param attributes список атрибутов (метрики, измерения) для формирования фильтра.
     * @param limit      количество условий в фильтре.
     * @return строка - фильтр.
     */
    public String getAnalyticsFilterWithAttributes(List<String> attributes, int limit) {
        return getAnalyticsFilterExpressionWithAttributes(attributes, limit).build(REPORT_TYPE);
    }

    public Expression getAnalyticsFilterExpressionWithAttributes(List<String> attributes, int limit) {
        return attributes.subList(0, limit).stream()
                .map(attribute -> (Expression) Term.term(attribute).equalTo(1))
                .reduce(empty(), Expression::and);
    }
}
