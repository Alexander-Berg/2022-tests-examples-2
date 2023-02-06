package ru.yandex.autotests.metrika.appmetrica.tests.b2b;

import java.util.Collection;

import com.google.common.collect.ImmutableList;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.metrika.appmetrica.data.Application;
import ru.yandex.autotests.metrika.appmetrica.data.Users;
import ru.yandex.autotests.metrika.appmetrica.parameters.CACohortType;
import ru.yandex.autotests.metrika.appmetrica.parameters.CAConversion;
import ru.yandex.autotests.metrika.appmetrica.parameters.CAGroup;
import ru.yandex.autotests.metrika.appmetrica.parameters.CAMetric;
import ru.yandex.autotests.metrika.appmetrica.parameters.CARetention;
import ru.yandex.autotests.metrika.appmetrica.parameters.CohortAnalysisParameters;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.autotests.metrika.commons.junitparams.combinatorial.CombinatorialBuilder;
import ru.yandex.metrika.mobmet.cohort.model.CAResponse;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.appmetrica.data.Application.ID;
import static ru.yandex.autotests.metrika.appmetrica.data.Applications.DRIVE;
import static ru.yandex.autotests.metrika.appmetrica.data.ParallellismUtils.resetCurrentLayer;
import static ru.yandex.autotests.metrika.appmetrica.data.ParallellismUtils.setCurrentLayerByApp;
import static ru.yandex.autotests.metrika.appmetrica.matchers.B2BMatchers.similarTo;
import static ru.yandex.autotests.metrika.appmetrica.parameters.CACohortType.someApiDimension;
import static ru.yandex.autotests.metrika.appmetrica.parameters.CACohortType.apiDimensions;
import static ru.yandex.autotests.metrika.appmetrica.parameters.CACohortType.installationDate;
import static ru.yandex.autotests.metrika.appmetrica.parameters.CACohortType.partner;
import static ru.yandex.autotests.metrika.appmetrica.parameters.CACohortType.tracker;
import static ru.yandex.autotests.metrika.appmetrica.parameters.CACohortType.trackerParam;
import static ru.yandex.autotests.metrika.appmetrica.parameters.CAConversion.anyActivity;
import static ru.yandex.autotests.metrika.appmetrica.parameters.CAConversion.sessionStart;
import static ru.yandex.autotests.metrika.appmetrica.parameters.CAConversion.toEventLabel;
import static ru.yandex.autotests.metrika.appmetrica.properties.AppMetricaApiProperties.apiProperties;
import static ru.yandex.autotests.metrika.appmetrica.steps.UserSteps.assumeOnCaResponses;

@Features(Requirements.Feature.DATA)
@Stories(Requirements.Story.COHORT_ANALYSIS)
@Title("Когортный анализ (сравнение)")
@RunWith(Parameterized.class)
public final class CAComparisonTest {
    private static final UserSteps testingSteps = UserSteps.builder()
            .withBaseUrl(apiProperties().getApiTesting())
            .withUser(Users.SUPER_LIMITED)
            .build();

    private static final UserSteps referenceSteps = UserSteps.builder()
            .withBaseUrl(apiProperties().getApiReference())
            .withUser(Users.SUPER_LIMITED)
            .build();

    /**
     * Возьмём приложение со второго слоя чтобы было меньше блокировок
     */
    private static final Application APP = DRIVE;
    private static final String SOME_EVENT_LABEL = "chat_shown";
    private static final String SOME_TRACKER_PARAM = "utm_source";
    /**
     * Тестируем только одну валюту, потому что ручка тяжёлая, и тесты долго выполняются.
     */
    private static final String[] CURRENCIES = new String[]{"EUR"};
    private static final String[] NO_CURRENCIES = new String[]{null};

    @Parameterized.Parameter
    public CACohortType cohortType;

    @Parameterized.Parameter(1)
    public CAMetric metric;

    @Parameterized.Parameter(2)
    public CARetention retention;

    @Parameterized.Parameter(3)
    public CAGroup group;

    @Parameterized.Parameter(4)
    public CAConversion conversion;

    @Parameterized.Parameter(5)
    public String currency;

    private IFormParameters parameters;

    @Parameterized.Parameters(name = "CohortType: {0}. Metric: {1}. Retention: {2}. Group: {3}. Conversion: {4}. Currency: {5}")
    public static Iterable<Object[]> createParameters() {

        // Проверяем трекинговые типы когорт
        Collection<Object[]> caTests = CombinatorialBuilder.builder()
                .values(installationDate(), tracker(), partner(), trackerParam(SOME_TRACKER_PARAM))
                .values(CAMetric.EVENT_METRICS.toArray())
                .values(CARetention.EMPTY)
                .values(CAGroup.values())
                .values(sessionStart(), toEventLabel(SOME_EVENT_LABEL))
                .values(NO_CURRENCIES)
                .build();

        // Проверяем revenue-метрики
        Collection<Object[]> caRevenueTests = CombinatorialBuilder.builder()
                .values(installationDate(), tracker(), partner(), trackerParam(SOME_TRACKER_PARAM))
                .values(CAMetric.REVENUE_METRICS.toArray())
                .values(CARetention.EMPTY)
                .values(CAGroup.values())
                .values(anyActivity())
                .values(CURRENCIES)
                .build();

        // Проверяем retention
        Collection<Object[]> retentionTests = CombinatorialBuilder.builder()
                .values(installationDate(), tracker(), partner(), trackerParam(SOME_TRACKER_PARAM))
                .values(CAMetric.DEVICES)
                .values(CARetention.CLASSIC, CARetention.ROLLING)
                .values(CAGroup.values())
                .values(sessionStart(), toEventLabel(SOME_EVENT_LABEL))
                .values(NO_CURRENCIES)
                .build();

        // Проверяем cohortType=api_dimension со всеми группировками и минимальной комбинацией остальных параметров
        Collection<Object[]> caAllApiDimensionsTests = CombinatorialBuilder.builder()
                .values(apiDimensions())
                .values(CAMetric.EVENTS)
                .values(CARetention.EMPTY)
                .values(CAGroup.DAY)
                .values(sessionStart())
                .values(NO_CURRENCIES)
                .build();

        // Проверяем cohortType=api_dimension с произвольной группировкой и всеми комбинациями остальных параметров
        Collection<Object[]> caSomeApiDimensionTests = CombinatorialBuilder.builder()
                .values(someApiDimension())
                .values(CAMetric.EVENT_METRICS.toArray())
                .values(CARetention.EMPTY)
                .values(CAGroup.values())
                .values(sessionStart(), toEventLabel(SOME_EVENT_LABEL))
                .values(NO_CURRENCIES)
                .build();

        // Проверяем cohortType=api_dimension с произвольной группировкой и всеми комбинациями revenue-метрик
        Collection<Object[]> caSomeApiDimensionRevenueTests = CombinatorialBuilder.builder()
                .values(someApiDimension())
                .values(CAMetric.REVENUE_METRICS.toArray())
                .values(CARetention.EMPTY)
                .values(CAGroup.values())
                .values(anyActivity())
                .values(CURRENCIES)
                .build();

        return ImmutableList.<Object[]>builder()
                .addAll(caTests)
                .addAll(caRevenueTests)
                .addAll(retentionTests)
                .addAll(caAllApiDimensionsTests)
                .addAll(caSomeApiDimensionTests)
                .addAll(caSomeApiDimensionRevenueTests)
                .build();
    }

    @Before
    public void setup() {
        setCurrentLayerByApp(APP.get(ID));
        parameters = new CohortAnalysisParameters()
                .withId(APP.get(ID))
                .withDate1(apiProperties().getCaStartDate())
                .withDate2(apiProperties().getCaEndDate())
                .withAccuracy("0.1")
                .withCohortType(cohortType)
                .withMetric(metric)
                .withRetention(retention)
                .withGroup(group)
                .withConversion(conversion)
                .withCurrency(currency)
                .withLang("ru")
                .withRequestDomain("ru");
    }

    @Test
    public void checkReportsMatch() {
        final CAResponse testingData = testingSteps.onCohortAnalysisSteps().getReportUnwrapped(parameters);
        final CAResponse referenceData = referenceSteps.onCohortAnalysisSteps().getReportUnwrapped(parameters);

        assumeOnCaResponses(testingData, referenceData);

        assertThat("отчеты совпадают", testingData, similarTo(referenceData));
    }

    @After
    public void teardown() {
        resetCurrentLayer();
    }
}
