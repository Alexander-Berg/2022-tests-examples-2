package ru.yandex.autotests.metrika.matchers;

import org.hamcrest.Matcher;
import org.hamcrest.number.IsCloseTo;
import ru.yandex.autotests.irt.testutils.matchers.OrderMatcher;
import ru.yandex.autotests.metrika.data.metadata.v1.enums.ParametrizationTypeEnum;
import ru.yandex.metrika.segments.site.parametrization.Attribution;

import java.util.Collection;

import static org.hamcrest.Matchers.*;
import static org.hamcrest.core.Every.everyItem;
import static ru.yandex.autotests.irt.testutils.beandiffer.BeanDifferMatcher.beanEquivalent;
import static ru.yandex.autotests.irt.testutils.beandiffer.beanconstraint.BeanConstraints.ignore;

/**
 * Created by konkov on 26.12.2014.
 * <p/>
 * Контейнер различных матчеров, которые часто используются в тестах
 */
public class Matchers {

    /**
     * @return матчер по массиву строк, который содержит значения измерений,
     * осуществляет проверку на их заполненность
     */
    public static Matcher<Iterable<? super String>> iterableHasDimensionValuesFilled() {
        return not(anyOf(
                hasItem(nullValue(String.class)),
                hasItem(""),
                hasItem(equalToIgnoringCase("NaN")),
                hasItem(equalToIgnoringCase("-NaN"))));
    }

    /**
     * @return матчер по массиву строк, который содержит значения измерений,
     * осуществляет проверку на их заполненность, допуская значение null.
     */
    public static Matcher<Iterable<? super String>> iterableHasDimensionValuesFilledAllowNull() {
        return not(anyOf(
                hasItem(""),
                hasItem(equalToIgnoringCase("NaN")),
                hasItem(equalToIgnoringCase("-NaN"))));
    }

    /**
     * @return матчер по массиву строк, который содержит значения измерений,
     * осуществляет проверку на их заполненность, допуская значение null и пустую строку
     */
    public static Matcher<Iterable<? super String>> iterableHasDimensionValuesFilledAllowNullOrEmpty() {
        return not(anyOf(
                hasItem(equalToIgnoringCase("NaN")),
                hasItem(equalToIgnoringCase("-NaN"))));
    }

    /**
     * @return матчер по массиву значений метрик
     */
    public static Matcher<Iterable<Double>> iterableHasMetricValues() {
        return everyItem(anyOf(nullValue(Double.TYPE), isA(Double.TYPE)));
    }

    /**
     * @return матчер, на строки - непараметризованные измерения и метрики.
     */
    public static Matcher<String> notParameterized() {
        return not(anyOf(
                containsString(ParametrizationTypeEnum.ATTRIBUTION.getPlaceholder()),
                containsString(ParametrizationTypeEnum.GOAL_ID.getPlaceholder()),
                containsString(ParametrizationTypeEnum.GROUP.getPlaceholder()),
                containsString(ParametrizationTypeEnum.QUANTILE.getPlaceholder()),
                containsString(ParametrizationTypeEnum.CURRENCY.getPlaceholder())));
    }

    public static Matcher<String> parameterized(ParametrizationTypeEnum parametrization) {
        return containsString(parametrization.getPlaceholder());
    }

    /**
     * @param expected ожидаемое значение атрибуции
     * @return матчер для значения атрибуции, если ожидаемое значение атрибуции не задано, по умолчанию - lastsign
     */
    public static Matcher<Attribution> attributionEqualTo(Attribution expected) {
        return expected != null
                ? equalTo(expected)
                : equalTo(Attribution.LASTSIGN);
    }


    /**
     * Variant of {@link org.hamcrest.Matchers#closeTo(double, double)} with relative error support
     * @param operand operand
     * @param error error
     * @param relative whether error is relative
     * @return matcher
     */
    public static Matcher<java.lang.Double> closeTo(double operand, double error, boolean relative) {
        if (relative) {
            error = error * Math.abs(operand);
        }
        error = Math.max(error, 1e-7);
        return IsCloseTo.closeTo(operand, error);
    }

    /**
     * @param orderMatcher matcher to define general order
     * @return matcher that checks ordering of strings in collection using UTF-8 rules
     */
    public static Matcher<Collection<String>> isUtf8Ordered(OrderMatcher orderMatcher) {
        return new Utf8StringOrderMatcher(orderMatcher);
    }

}
