package ru.yandex.autotests.metrika.tests.ft.internal;

import org.junit.Test;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.parameters.internal.GetAccuracyParameters;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Title;

import static ru.yandex.autotests.irt.testutils.beandiffer.BeanDifferMatcher.beanEquivalent;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

/**
 * Created by omatikaya on 24.03.17.
 */
@Features(Requirements.Feature.INTERNAL)
@Title("Позитивные тесты на ручку get_accuracy/global для сводки")
public class AccuracyGlobalPositiveTest {
    private final static String START_DATE = "2017-02-20";
    private final static String ONE_DAY_END_DATE = "2017-02-20";
    private final static String ONE_WEEK_END_DAY = "2017-02-26";

    private final static Double ONE_DAY_ACCURACY = 1E-2;
    private final static Double ONE_WEEK_ACCURACY = 1E-3;

    private UserSteps user = new UserSteps();

    @Test
    public void checkOneDayAccuracyGlobalValue(){
        double result = user.onInternalSteps().getAccuracyGlobalAndExpectSuccess(
                new GetAccuracyParameters()
                        .withDate1(START_DATE)
                        .withDate2(ONE_DAY_END_DATE));

        assertThat("полученное значение точности совпадает с ожидаемым",
                result, beanEquivalent(ONE_DAY_ACCURACY));
    }

    @Test
    public void checkOneWeekAccuracyGlobalValue(){
        double result = user.onInternalSteps().getAccuracyGlobalAndExpectSuccess(
                new GetAccuracyParameters()
                        .withDate1(START_DATE)
                        .withDate2(ONE_WEEK_END_DAY));

        assertThat("полученное значение точности совпадает с ожидаемым",
                result, beanEquivalent(ONE_WEEK_ACCURACY));
    }
}
