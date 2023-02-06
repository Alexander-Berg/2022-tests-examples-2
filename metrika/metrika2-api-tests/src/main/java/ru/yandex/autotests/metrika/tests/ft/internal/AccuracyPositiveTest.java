package ru.yandex.autotests.metrika.tests.ft.internal;

import java.util.Arrays;
import java.util.List;
import java.util.concurrent.atomic.AtomicInteger;

import org.junit.Test;

import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.parameters.internal.GetAccuracyParameters;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.autotests.metrika.utils.Try;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Title;

import static java.util.Arrays.asList;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.isIn;
import static ru.yandex.autotests.metrika.data.common.CounterConstants.NO_DATA;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.TEST_DELEGATE_COUNTER;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.TEST_EDIT_PERMISSION_COUNTER;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.TEST_VIEW_PERMISSION_COUNTER;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.YANDEX_MARKET;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

/**
 * Created by ava1on on 12.09.16.
 */

@Features(Requirements.Feature.INTERNAL)
@Title("Позитивные тесты на ручку get_accuracy для сводки")
public class AccuracyPositiveTest {
    private final static String START_DATE = "2010-01-01";
    private final static String END_DATE = "2016-05-01";
    private final static List<Double> ACCURACY_VALUES = asList(1E-2, 1E-3, 1E-4);
    private final static Double accuracy = 1d;

    private UserSteps user = new UserSteps();

    @Test
    public void checkAccuracyValueForMarket(){
        double result = getAccuracy(YANDEX_MARKET);

        assertThat("полученное значение точности совпадает с ожидаемым",
                result, isIn(ACCURACY_VALUES));
    }

    @Test
    public void checkAccuracyValueForNoData() {
        // т.к логика для accuracy кешируется и в случае не успешных походов в mtAggr возвращает дефолт, пробуем брать значение для нескольких счетчиков.
        // если хотя бы для одного отрабатывает, то считаем что тест прошел
        List<Counter> counters = Arrays.asList(NO_DATA, TEST_DELEGATE_COUNTER, TEST_VIEW_PERMISSION_COUNTER, TEST_EDIT_PERMISSION_COUNTER);
        AssertionError error = null;
        for (Counter counter : counters) {
            error = null;
            double result = getAccuracy(counter);
            try {
                assertThat("полученное значение точности совпадает с ожидаемым",
                        result, equalTo(accuracy));
                break;
            } catch (AssertionError e) {
                error = e;
            }
        }
        if (error != null) throw error;
    }

    private double getAccuracy(Counter counter) {
        return user.onInternalSteps().getAccuracyAndExpectSuccess(
                new GetAccuracyParameters()
                        .withId(counter)
                        .withDate1(START_DATE)
                        .withDate2(END_DATE));
    }
}
