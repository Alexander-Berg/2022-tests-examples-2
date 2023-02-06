package ru.yandex.autotests.metrika.tests.b2b.timezone;

import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.parameters.report.v1.CommonReportParameters;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static java.util.Arrays.asList;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.irt.testutils.beandiffer.BeanDifferMatcher.beanEquivalent;

/**
 * Created by sonick on 18.01.2019.
 */
@Features(Requirements.Feature.INTERNAL)
@Stories(Requirements.Story.Internal.TIME_ZONES)
@Title("B2B - Проверка ручки часовых поясов")
@RunWith(Parameterized.class)
public class B2bTimeZonesTest {

    private static final UserSteps userOnTest = new UserSteps().withDefaultAccuracy();
    private static final UserSteps userOnRef = new UserSteps().useReference().withDefaultAccuracy();

    @Parameterized.Parameter(0)
    public String lang;

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> createParameters() {
        return asList(new Object[][]{
                {"ru"},
                {"en"},
                {"tr"}
        });
    }

    @Test
    public void checkTimeZonesList() {
        Object referenceBean = userOnRef.onInternalSteps().getTimeZonesListAndExpectSuccess(
                new CommonReportParameters().withLang(lang));
        Object testingBean = userOnTest.onInternalSteps().getTimeZonesListAndExpectSuccess(
                new CommonReportParameters().withLang(lang));

        assertThat("часовые пояса эквивалентны", testingBean, beanEquivalent(referenceBean));
    }

}
