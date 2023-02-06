package ru.yandex.autotests.metrika.tests.b2b.metrika.particulars;

import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.handles.RequestTypes;
import ru.yandex.autotests.metrika.data.common.users.Users;
import ru.yandex.autotests.metrika.data.parameters.FreeFormParameters;
import ru.yandex.autotests.metrika.data.parameters.report.v1.TableReportParameters;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.autotests.metrika.tests.b2b.BaseB2bParticularTest;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static com.google.common.collect.ImmutableList.of;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.irt.testutils.beandiffer.BeanDifferMatcher.beanEquivalent;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.TEST_NO_CAMPAIGN_COUNTER;

/**
 * Проблема воспроизводится на достаточно редкой комбинации юзеров и счетчиков
 * надо чтобы в отчете директ-сводки не было ничего кроме чужих кампаний.
 * При этом пользователь зашит в UserSteps, а в базовых классах они определены статически, при этом
 * зачастую используются в статических методах createParameters. В общем не придумал ничего лучше
 * чем полностью переопределить метод {{@link ru.yandex.autotests.metrika.tests.b2b.BaseB2bTest#check()}}.
 */
@Features(Requirements.Feature.DATA)
@Stories(Requirements.Story.Report.MANUAL_SAMPLES)
@Title("B2B на отобранных вручную параметрах запросов")
public class ParticularsBannerB2bTest extends BaseB2bParticularTest {

    private static final UserSteps userOnTest = new UserSteps()
            .withUser(Users.SIMPLE_USER)
            .withDefaultAccuracy();
    private static final UserSteps userOnRef = new UserSteps()
            .useReference()
            .withUser(Users.SIMPLE_USER)
            .withDefaultAccuracy();

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> createParameters() {
        return of(
                createParams("METR-24189 parse [0,0] as Tuple(UInt8,UInt64)",
                        RequestTypes.TABLE,
                        new FreeFormParameters(),
                        new TableReportParameters()
                                .withId(TEST_NO_CAMPAIGN_COUNTER)
                                .withDate1("2016-11-12")
                                .withDate2("2017-01-20")
                                .withAccuracy("1.0")
                                .withDimension(of("ym:s:lastDirectClickOrder",
                                        "ym:s:lastDirectClickBanner",
                                        "ym:s:lastDirectPhraseOrCond"
                                ))
                                .withIncludeUndefined(true)
                                .withMetrics(of(
                                        "ym:s:bounceRate",
                                        "ym:s:pageDepth",
                                        "ym:s:avgVisitDurationSeconds",
                                        "ym:s:anyGoalConversionRate")))
        );
    }

    @Override
    public void check() {
        Object referenceBean = userOnRef.onReportSteps().getRawReport(requestType, reportParameters);
        Object testingBean = userOnTest.onReportSteps().getRawReport(requestType, reportParameters);

        userOnTest.onResultSteps().assumeSuccessBoth(testingBean, referenceBean);
        userOnTest.onResultSteps().assumeNotEmptyBoth(testingBean, referenceBean);

        assertThat("ответы совпадают", testingBean, beanEquivalent(referenceBean).fields(getIgnore()).withVariation(doubleWithAccuracy));
    }
}
