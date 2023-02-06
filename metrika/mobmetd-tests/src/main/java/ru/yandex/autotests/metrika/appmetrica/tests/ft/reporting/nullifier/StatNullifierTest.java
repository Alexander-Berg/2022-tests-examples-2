package ru.yandex.autotests.metrika.appmetrica.tests.ft.reporting.nullifier;

import com.google.common.collect.ImmutableList;
import org.hamcrest.Matcher;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.StatV1DataBytimeGETSchema;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.StatV1DataDrilldownGETSchema;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.StatV1DataGETSchema;
import ru.yandex.autotests.metrika.appmetrica.data.Application;
import ru.yandex.autotests.metrika.appmetrica.data.Applications;
import ru.yandex.autotests.metrika.appmetrica.data.Users;
import ru.yandex.autotests.metrika.appmetrica.parameters.TableReportParameters;
import ru.yandex.autotests.metrika.appmetrica.properties.AppMetricaApiProperties;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.metrika.api.constructor.response.DrillDownRow;
import ru.yandex.metrika.api.constructor.response.DynamicRow;
import ru.yandex.metrika.api.constructor.response.StaticRow;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;
import java.util.List;
import java.util.stream.Collectors;

import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.everyItem;
import static ru.yandex.autotests.metrika.appmetrica.data.ParallellismUtils.resetCurrentLayer;
import static ru.yandex.autotests.metrika.appmetrica.data.ParallellismUtils.setCurrentLayerByApp;
import static ru.yandex.autotests.metrika.appmetrica.properties.AppMetricaApiProperties.apiProperties;
import static ru.yandex.autotests.metrika.appmetrica.steps.UserSteps.assumeOnResponse;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.reporting.nullifier.NullifierUtils.NOT_NULL_ROW_MATCHER;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.reporting.nullifier.NullifierUtils.NULL_ROW_MATCHER;

@Features(Requirements.Feature.DATA)
@Stories(Requirements.Story.METRICS)
@Title("Зануление метрик при выборе несовместимых фильтров")
@RunWith(Parameterized.class)
public class StatNullifierTest {

    private static final UserSteps onTesting = UserSteps.builder()
            .withBaseUrl(apiProperties().getApiTesting())
            .withUser(Users.SUPER_LIMITED)
            .build();

    private static final Application APPLICATION = Applications.YANDEX_REALTY;

    @Parameterized.Parameter
    public boolean hideMetrics;

    @Parameterized.Parameter(1)
    public boolean hideBytimeTotals;

    @Parameterized.Parameter(2)
    public String dimensions;

    @Parameterized.Parameter(3)
    public String metrics;

    @Parameterized.Parameter(4)
    public String filter;

    private TableReportParameters requestParameters;

    private Matcher<Double> matcher;

    private Matcher<Double> bytimeTotalsMatcher;

    private String dataMessage;

    private String totalsMessage;

    private String bytimeTotalsMessage;

    @Parameterized.Parameters(name = "hide metrics={0}, hideBytimeTotals={1}, dimensions={2}, metrics={3}, filter={4}")
    public static Collection<Object[]> createParameters() {
        // В мобмете есть заглушка: при сегментации "по сессиям, в которых" должна зануляться метрика "новые пользователи".
        // Тестами проверяем, что при наличии атрибута session среди фильтров в ответе приходят null-ы.
        // totals bytime-а не учитывает запрашиваемые dimension-ы, поэтому должен быть обработан отдельно
        return ImmutableList.of(
                params(true, true, "ym:u:regionCountry", "ym:u:newUsers,ym:u:newUsersPercentage", "session!='1.1.1'"),
                params(true, true, "ym:u:regionCountry", "ym:u:newUsers,ym:u:newUsersPercentage", "ym:u:session!='1.1.1'"),
                params(true, true, "ym:u:regionCountry", "ym:u:newUsers,ym:u:newUsersPercentage", "ym:u:age == 25 AND ym:u:session!='1.1.1'"),
                params(true, true, "ym:u:regionCountry", "ym:u:newUsers,ym:u:newUsersPercentage", "ym:u:age == 25 OR ym:u:session!='1.1.1'"),
                params(true, true, "ym:u:regionCountry", "ym:u:newUsers,ym:u:newUsersPercentage", "exists ym:ge:session with (ym:ge:regionCountry == 225)"),
                params(false, false, "ym:u:regionCountry", "ym:u:newUsers,ym:u:newUsersPercentage", "ym:u:age == 25"),
                params(false, false, "ym:u:regionCountry", "ym:u:newUsers,ym:u:newUsersPercentage", "exists ym:ge:user with (ym:ge:age == 25)"),
                params(false, false, "ym:u:regionCountry", "ym:u:newUsers,ym:u:newUsersPercentage", "exists ym:ge:user with (ym:ge:session!='1.1.1')"),

                params(true, false, "ym:ts:ageInterval", "ym:ts:userClicks", ""),
                params(true, false, "ym:ts:gender", "ym:ts:userClicks", ""),
                params(true, false, "ym:ts:installSourceType", "ym:ts:userClicks", ""),

                // в кликах есть устройства с неправильными партнёрами, поэтому они зануляются самой метрикой
                params(true, true, "ym:ts:buildNumber", "ym:ts:userConversion", ""),
                params(true, true, "ym:ts:appVersion", "ym:ts:openConversion", ""),
                params(true, true, "ym:ts:appVersion", "ym:ts:remarketingConversion", ""),

                params(true, true, "ym:ts:regionCountry", "ym:ts:userClicks", "appVersion!='1111'"),
                params(false, false, "ym:ts:regionCountry", "ym:ts:userClicks", "")
        );
    }

    @Before
    public void prepareRequestParams() {
        setCurrentLayerByApp(APPLICATION);
        requestParameters = new TableReportParameters()
                .withId(APPLICATION.get(Application.ID))
                .withDate1(AppMetricaApiProperties.apiProperties().getDefaultStartDate())
                .withDate2(AppMetricaApiProperties.apiProperties().getDefaultEndDate())
                .withAccuracy("0.05")
                .withDimension(dimensions)
                .withMetrics(ImmutableList.of(metrics))
                .withFilters(filter);

        matcher = hideMetrics ? NULL_ROW_MATCHER : NOT_NULL_ROW_MATCHER;
        bytimeTotalsMatcher = hideBytimeTotals ? NULL_ROW_MATCHER : NOT_NULL_ROW_MATCHER;
        dataMessage = hideMetrics ? "Метрики занулились" : "Метрики не занулились";
        totalsMessage = hideMetrics ? "Метрики в totals занулились" : "Метрики в totals не занулились";
        bytimeTotalsMessage = hideBytimeTotals ? "Метрики в totals занулились" : "Метрики в totals не занулились";
    }

    @Test
    public void checkMetricsHidingTable() {
        StatV1DataGETSchema report = onTesting.onReportSteps().getTableReport(requestParameters);

        assumeOnResponse(report);
        assertThat(dataMessage,
                report.getData().stream()
                        .map(StaticRow::getMetrics)
                        .collect(Collectors.toList()),
                everyItem(everyItem(matcher)));
        assertThat(totalsMessage, report.getTotals(), everyItem(matcher));
    }

    @Test
    public void checkMetricsHidingDrilldown() {
        StatV1DataDrilldownGETSchema report = onTesting.onReportSteps().getDrillDownReport(requestParameters);

        assumeOnResponse(report);
        assertThat(dataMessage,
                report.getData().stream()
                        .map(DrillDownRow::getMetrics)
                        .collect(Collectors.toList()),
                everyItem(everyItem(matcher)));
        assertThat(totalsMessage, report.getTotals(), everyItem(matcher));
    }

    @Test
    public void checkMetricsHidingBytime() {
        StatV1DataBytimeGETSchema report = onTesting.onReportSteps().getByTimeReport(requestParameters);

        assumeOnResponse(report);

        // немножко приведений типов, чтобы matcher-ы были нами довольны
        List<Iterable<Iterable<Double>>> dataMetrics = report.getData().stream()
                .map(DynamicRow::getMetrics)
                .map(NullifierUtils::toIterable)
                .collect(Collectors.toList());
        List<Iterable<Double>> totalsMetrics = NullifierUtils.toIterable(report.getTotals());

        assertThat(dataMessage, dataMetrics, everyItem(everyItem(everyItem(matcher))));
        assertThat(bytimeTotalsMessage, totalsMetrics, everyItem(everyItem(bytimeTotalsMatcher)));
    }

    @After
    public void teardown() {
        resetCurrentLayer();
    }

    private static Object[] params(boolean nullify, boolean nullifyBytimeTotals, String dimensions, String metrics, String filter) {
        return new Object[]{nullify, nullifyBytimeTotals, dimensions, metrics, filter};
    }
}
