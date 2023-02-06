package ru.yandex.autotests.metrika.appmetrica.tests.b2b;

import java.util.Collection;
import java.util.List;
import java.util.stream.Collectors;
import java.util.stream.Stream;

import com.google.common.collect.ImmutableList;
import com.google.common.collect.ImmutableList.Builder;
import com.google.common.collect.Iterables;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;

import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.metrika.appmetrica.core.ParallelizedParameterized;
import ru.yandex.autotests.metrika.appmetrica.data.Users;
import ru.yandex.autotests.metrika.appmetrica.parameters.CAReportParameters;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.autotests.metrika.commons.junitparams.combinatorial.CombinatorialBuilder;
import ru.yandex.metrika.api.cohort.response.model.CAResponse;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.appmetrica.data.Application.ID;
import static ru.yandex.autotests.metrika.appmetrica.data.Applications.PLANETAZDOROVO;
import static ru.yandex.autotests.metrika.appmetrica.data.ParallellismUtils.resetCurrentLayer;
import static ru.yandex.autotests.metrika.appmetrica.data.ParallellismUtils.setCurrentLayerByApp;
import static ru.yandex.autotests.metrika.appmetrica.matchers.B2BMatchers.similarTo;
import static ru.yandex.autotests.metrika.appmetrica.properties.AppMetricaApiProperties.apiProperties;
import static ru.yandex.autotests.metrika.appmetrica.steps.UserSteps.assumeOnCaV2Responses;

@Features(Requirements.Feature.DATA)
@Stories({
        Requirements.Story.DIMENSIONS,
        Requirements.Story.COHORT_ANALYSIS_V2
})
@Title("Cohort B2B")
@RunWith(ParallelizedParameterized.class)
public class B2bCohortAnalysisTest {

    private static final UserSteps testingSteps = UserSteps.builder()
            .withBaseUrl(apiProperties().getApiTesting())
            .withUser(Users.SUPER_LIMITED)
            .build();

    private static final UserSteps referenceSteps = UserSteps.builder()
            .withBaseUrl(apiProperties().getApiReference())
            .withUser(Users.SUPER_LIMITED)
            .build();

    private static final long APP_ID = PLANETAZDOROVO.get(ID);
    private static final String EVENT_NAME = "Т_002_таб_поиск";

    /**
     * В API есть лимит на количество одновременно запрошенных метрик.
     * Будем его соблюдать.
     */
    private static final int METRIC_LIMIT = 10;

    @Parameterized.Parameter()
    public String title;

    @Parameterized.Parameter(1)
    public IFormParameters parameters;

    private static final List<Metric> METRICS = ImmutableList.<Metric>builder()
            // session starts
            .addAll(retentionMetrics("ym:ge:", "userRetention"))
            .addAll(retentionMetrics("ym:ge:", "userRollingRetention"))
            .add(Metric.of("ym:ge:", "sessionStarts"))
            .add(Metric.of("ym:ge:", "avgSessionStarts"))
            // client events
            .addAll(retentionMetrics("ym:ce:", "clientEventRetention<event_name>"))
            .addAll(retentionMetrics("ym:ce:", "clientEventRollingRetention<event_name>"))
            .add(Metric.of("ym:ce:", "clientEvents<event_name>"))
            .add(Metric.of("ym:ce:", "avgClientEvents<event_name>"))
            .add(Metric.of("ym:ce:", "clientEventDevices<event_name>"))
            .add(Metric.of("ym:ce:", "clientEventDevices<event_name>Percentage"))
            // revenue
            .addAll(retentionMetrics("ym:r:", "purchaseRetention"))
            .addAll(retentionMetrics("ym:r:", "purchaseRollingRetention"))
            .add(Metric.of("ym:r:", "purchases"))
            .add(Metric.of("ym:r:", "avgPurchases"))
            .add(Metric.of("ym:r:", "payingUsers"))
            .add(Metric.of("ym:r:", "payingUsersPercentage"))
            .add(Metric.of("ym:r:", "revenue<currency>"))
            .add(Metric.of("ym:r:", "averageRevenue<currency>PerUser"))
            .add(Metric.of("ym:r:", "averageRevenue<currency>PerPayingUser"))
            // engagement
            .add(Metric.of("ym:ge:", "timeSpent"))
            .add(Metric.of("ym:ge:", "avgTimeSpent"))
            .build();

    private static final Metric ANY_METRIC = METRICS.get(0);

    private static List<Metric> retentionMetrics(String ns, String name) {
        return List.of(
                Metric.of(ns, name + "Realtime"),
                Metric.of(ns, name + "Status"),
                Metric.of(ns, name + "Percentage"));
    }

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> createParameters() {
        Builder<Object[]> builder = ImmutableList.builder();

        METRICS.stream()
                .collect(Collectors.groupingBy(Metric::ns))
                .forEach((ns, metrics) -> {
                    // Проверяем корректность выражений метрик и генерацию FROM из разных таблиц
                    // с restriction condition в WHERE.
                    Iterables.partition(metrics, METRIC_LIMIT).forEach(metricsPart -> {
                        List<String> metricApiNames = metricsPart.stream()
                                .map(Metric::getApiName)
                                .toList();
                        builder.add(params("Метрики " + metricApiNames, defaultRequestParams()
                                .withDimension("ym:i:publisher")
                                .withMetrics(metricApiNames)));
                    });

                    // Тестим комбинации group_method и group: смотрим, работает ли выражение номера conversion period
                    // в разных метричных неймспейсах
                    Metric anyMetricFromNs = metrics.get(0);
                    CombinatorialBuilder.builder()
                            .values("calendar", "window")
                            .values("day", "week", "month")
                            .build().forEach(combo -> {
                                String groupMethod = (String) combo[0];
                                String group = (String) combo[1];
                                builder.add(params("group_method: " + groupMethod + ", group: " + group,
                                        defaultRequestParams()
                                                // Большие номера периодов не передаём, чтобы диапазон EventDate
                                                // в подзапросе за конверсиями для group=month не был слишком широким.
                                                .withBrackets("0,1,2")
                                                .withGroupMethod(groupMethod)
                                                .withGroup(group)
                                                .withDimension("ym:i:publisher")
                                                .withMetric(anyMetricFromNs.getApiName())));
                            });
                });

        // Дефолтный brackets
        builder.add(params("default &brackets=", defaultRequestParams()
                // По умолчанию КА строится до today, либо упирается в лимит 100 колонок.
                // Нужно упереться в лимит, чтобы запросы к api и ref дали одинаковый результат,
                // поэтому подбираем достаточно старые даты и используем &group=day
                .withBrackets(null)
                .withGroup("day")
                .withDate1("2021-11-01")
                .withDate1("2021-11-07")
                .withDimension("ym:i:publisher")
                .withMetric(ANY_METRIC.getApiName())));

        // Недефолтная сортировка по метрике, например по брекету с индексом 2:
        String sortMetric = "-" + ANY_METRIC.getApiName() + "2";
        builder.add(params("sort with &sort=" + sortMetric, defaultRequestParams()
                .withBrackets("0,1,4")
                .withDimension("ym:i:publisher")
                .withMetric(ANY_METRIC.getApiName())
                .withSort(sortMetric)));

        // Два параметра одной группировки
        builder.add(params("2 url params", defaultRequestParams()
                .withUrlParameterKey("campaignId")
                .withUrlParameterKey1("conversionType")
                .withDimensions(List.of(
                        "ym:i:urlParameter<url_parameter_key>",
                        "ym:i:urlParameter<url_parameter_key_1>"
                ))
                .withMetric(ANY_METRIC.getApiName())
                .withDate1("2021-11-12")
                .withDate2("2021-11-25")
                .withAccuracy("1.0")));

        // Треугольная таблица
        Stream.of("ym:i:date", "ym:i:startOfWeek", "ym:i:startOfMonth")
                .forEach(dim -> Stream.of("window", "calendar")
                        .forEach(groupMethod -> builder.add(params("triangle " + groupMethod + " table, " + dim,
                                defaultRequestParams()
                                        .withBrackets(null)
                                        .withGroupMethod(groupMethod)
                                        .withDimension(dim)
                                        .withMetric(ANY_METRIC.getApiName())
                        ))));

        return builder.build();
    }

    private static Object[] params(String title, IFormParameters requestParams) {
        return new Object[]{title, requestParams};
    }

    private static CAReportParameters defaultRequestParams() {
        return (CAReportParameters) new CAReportParameters()
                .withGroup("day")
                .withGroupMethod("calendar")
                .withBrackets("0,1,2-7,28")
                .withEventName(EVENT_NAME)
                .withId(APP_ID)
                .withDimension("ym:i:publisher")
                .withMetric(ANY_METRIC.getApiName())
                .withDate1("2021-11-01")
                .withDate2("2021-11-07")
                .withAccuracy("0.1");
    }

    @Before
    public void setup() {
        setCurrentLayerByApp(APP_ID);
    }

    @Test
    public void checkReportsMatch() {
        CAResponse testingData = testingSteps.onCohortAnalysisV2Steps().getReport(parameters);
        CAResponse referenceData = referenceSteps.onCohortAnalysisV2Steps().getReport(parameters);

        assumeOnCaV2Responses(testingData, referenceData);

        assertThat("отчеты совпадают", testingData, similarTo(referenceData));
    }

    @After
    public void teardown() {
        resetCurrentLayer();
    }

    private static record Metric(String ns, String name) {
        public static Metric of(String ns, String name) {
            return new Metric(ns, name);
        }

        public String getApiName() {
            return ns + name;
        }
    }
}
