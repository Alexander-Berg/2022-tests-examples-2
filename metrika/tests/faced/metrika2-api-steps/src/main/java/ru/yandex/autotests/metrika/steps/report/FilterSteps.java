package ru.yandex.autotests.metrika.steps.report;

import ru.yandex.autotests.httpclient.lite.core.steps.BackEndBaseSteps;
import ru.yandex.autotests.metrika.filters.Expression;
import ru.yandex.autotests.metrika.filters.Operator;
import ru.yandex.autotests.metrika.filters.Term;
import ru.yandex.autotests.metrika.filters.user.Condition;
import ru.yandex.autotests.metrika.filters.user.ConditionSequence;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import static java.util.stream.IntStream.range;
import static org.apache.commons.lang3.StringUtils.EMPTY;
import static ru.yandex.autotests.metrika.filters.Term.*;
import static ru.yandex.autotests.metrika.filters.user.User.cond;

/**
 * Created by konkov on 27.05.2015.
 */
public class FilterSteps extends BackEndBaseSteps {

    /**
     * Формирует фильтр на каждый из переданных атрибутов, но не более указанного количества условий.
     *
     * @param attributes список атрибутов (метрики, измерения) для формирования фильтра.
     * @param limit      количество условий в фильтре.
     * @return строка - фильтр.
     */
    public String getFilterWithAttributes(Collection<String> attributes, int limit) {
        return getFilterExpressionWithAttributes(attributes, limit).build();
    }

    public Expression getFilterExpressionWithAttributes(Collection<String> attributes, int limit) {
        return attributes.stream()
                .limit(limit)
                .map(attribute -> (Expression) term(attribute).equalTo(1))
                .reduce(empty(), Expression::and);
    }

    /**
     * Формирует фильтр с одним атрибутом и заданным количеством условий.
     *
     * @param conditionAttribute атрибут для формирования фильтра (метрика, измерение).
     * @param numberOfConditions количество условий в фильтре.
     * @return строка - фильтр.
     */
    public String getFilterWithConditions(String conditionAttribute, int numberOfConditions) {
        return getFilterExpressionWithConditions(conditionAttribute, numberOfConditions).build();
    }

    public Expression getFilterExpressionWithConditions(String conditionAttribute, int numberOfConditions) {
        return range(0, numberOfConditions)
                .mapToObj(i -> (Expression) term(conditionAttribute).equalTo(i))
                .reduce(empty(), Expression::or);
    }

    /**
     * Формирует фильтр с одним атрибутом и одним условием с заданной длиной.
     *
     * @param conditionAttribute атрибут для формирования фильтра (метрика, измерение).
     * @param length             длина условия.
     * @return строка - фильтр.
     */
    public String getFilterWithSingleCondition(String conditionAttribute, int length) {
        Term filter = term(conditionAttribute).equalTo(EMPTY);
        StringBuilder operandStringBuilder = new StringBuilder();
        int tail = filter.build().length();
        for (int i = 0; i < length - tail; i++) {
            operandStringBuilder.append('X');
        }
        return filter.equalTo(operandStringBuilder.toString()).build();
    }

    public String getTopLevelOrCombination() {
        return dimension("ym:s:endURL").equalTo(EMPTY)
                .or(metric("ym:s:newUsers").equalTo(0)).build();
    }

    public String getTopLevelAndCombination() {
        return dimension("ym:s:endURL").equalTo(EMPTY)
                .and(metric("ym:s:newUsers").equalTo(0)).build();
    }

    public String getAllowedNestedCombination() {
        return dimension("ym:s:endURL").equalTo(EMPTY)
                .or(dimension("ym:s:startURL").equalTo("X"))
                .and(metric("ym:s:newUsers").equalTo(0)).build();
    }

    public String getDisallowedNestedCombination() {
        return dimension("ym:s:startURL").equalTo("X")
                .and(metric("ym:s:newUsers").equalTo(1))
                .or(metric("ym:s:users").equalTo(0).and(dimension("ym:s:endURL").equalTo(EMPTY))).build();
    }

    public ConditionSequence getConditionSequence(int maximumAllowedCond) {
        Condition c = cond("ym:s", dimension("ym:s:browser").equalTo(1));
        for (int i = 1; i < maximumAllowedCond; i++) {
            c = c.any().cond("ym:s", dimension("ym:s:browser").equalTo(1));
        }
        return c;
    }

    public String getMultiOperandFilter(String dimensionName, Operator operator, int numberOfOperands) {
        List<Integer> operand = new ArrayList<>();
        for (int i = 1; i <= numberOfOperands; i++) {
            operand.add(i);
        }

        return term(dimensionName)
                .withOperator(operator)
                .withOperand(operand)
                .build();

    }
}
