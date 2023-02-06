package ru.yandex.autotests.metrika.appmetrica.tests.ft.reporting.nullifier;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.StatV1DataBytimeGETSchema;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.StatV1DataDrilldownGETSchema;
import ru.yandex.autotests.metrika.appmetrica.data.Application;
import ru.yandex.autotests.metrika.appmetrica.data.Applications;
import ru.yandex.autotests.metrika.appmetrica.data.Users;
import ru.yandex.autotests.metrika.appmetrica.parameters.BytimeReportParameters;
import ru.yandex.autotests.metrika.appmetrica.parameters.DrillDownReportParameters;
import ru.yandex.autotests.metrika.appmetrica.properties.AppMetricaApiProperties;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.metrika.api.constructor.response.DrillDownRow;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Arrays;
import java.util.Collections;
import java.util.stream.Collectors;

import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.everyItem;
import static org.hamcrest.core.IsEqual.equalTo;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assumeThat;
import static ru.yandex.autotests.metrika.appmetrica.data.ParallellismUtils.resetCurrentLayer;
import static ru.yandex.autotests.metrika.appmetrica.data.ParallellismUtils.setCurrentLayerByApp;
import static ru.yandex.autotests.metrika.appmetrica.properties.AppMetricaApiProperties.apiProperties;
import static ru.yandex.autotests.metrika.appmetrica.steps.UserSteps.assumeOnResponse;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.reporting.nullifier.NullifierUtils.*;

/**
 * У drilldown и bytime есть параметры с особой логикой (row_ids, parent_id), которые лучше
 * протестировать отдельно
 */
@Features(Requirements.Feature.DATA)
@Stories(Requirements.Story.METRICS)
@Title("Зануление метрик при выборе несовместимых фильтров в отдельных запросах")
public class StatNulliferSpecialTest {

    private static final UserSteps onTesting = UserSteps.builder()
            .withBaseUrl(apiProperties().getApiTesting())
            .withUser(Users.SUPER_LIMITED)
            .build();

    private static final Application APPLICATION = Applications.YANDEX_TRANSLATE_FOR_ANDROID;

    @Before
    public void prepareRequestParams() {
        setCurrentLayerByApp(APPLICATION);
    }

    @Test
    public void bytimeTest() {
        BytimeReportParameters parameters = new BytimeReportParameters()
                .withId(APPLICATION)
                .withRowIds("[[\"254\"],[\"254\",\"25\"]]")
                .withDimension("ym:ts:publisher,ym:ts:ageInterval")
                .withMetric("ym:ts:userClicks")
                .withDate1(AppMetricaApiProperties.apiProperties().getDefaultStartDate())
                .withDate2(AppMetricaApiProperties.apiProperties().getDefaultEndDate())
                .withAccuracy("0.1");

        StatV1DataBytimeGETSchema report = onTesting.onReportSteps().getByTimeReport(parameters);

        assumeOnResponse(report);

        assumeThat("Вернулось две строки", report.getData().size(), equalTo(2));

        assertThat("Первая строка не занулена",
                toIterable(report.getData().get(0).getMetrics()),
                everyItem(everyItem(NOT_NULL_ROW_MATCHER)));
        assertThat("Вторая строка занулена",
                toIterable(report.getData().get(1).getMetrics()),
                everyItem(everyItem(NULL_ROW_MATCHER)));
        assertThat("Totals не занулён",
                toIterable(report.getTotals()),
                everyItem(everyItem(NOT_NULL_ROW_MATCHER)));
    }

    @Test
    public void drilldownNonNullTest() {
        DrillDownReportParameters parameters = new DrillDownReportParameters()
                .withId(APPLICATION)
                .withParentIds(Collections.singletonList("254"))
                .withDimension("ym:ts:publisher,ym:ts:campaign,ym:ts:ageInterval")
                .withMetric("ym:ts:userClicks")
                .withDate1(AppMetricaApiProperties.apiProperties().getDefaultStartDate())
                .withDate2(AppMetricaApiProperties.apiProperties().getDefaultEndDate())
                .withAccuracy("0.1");

        StatV1DataDrilldownGETSchema report = onTesting.onReportSteps().getDrillDownReport(parameters);

        assumeOnResponse(report);

        assertThat("Данные не занулены",
                report.getData().stream()
                        .map(DrillDownRow::getMetrics)
                        .collect(Collectors.toList()),
                everyItem(everyItem(NOT_NULL_ROW_MATCHER)));
        assertThat("Totals не занулён", report.getTotals(), everyItem(NOT_NULL_ROW_MATCHER));
    }

    @Test
    public void drilldownNullTest() {
        DrillDownReportParameters parameters = new DrillDownReportParameters()
                .withId(APPLICATION)
                .withParentIds(Arrays.asList("254", "4272535375405217304"))
                .withDimension("ym:ts:publisher,ym:ts:campaign,ym:ts:ageInterval")
                .withMetric("ym:ts:userClicks")
                .withDate1(AppMetricaApiProperties.apiProperties().getDefaultStartDate())
                .withDate2(AppMetricaApiProperties.apiProperties().getDefaultEndDate())
                .withAccuracy("0.1");

        StatV1DataDrilldownGETSchema report = onTesting.onReportSteps().getDrillDownReport(parameters);

        assumeOnResponse(report);

        assertThat("Данные занулены",
                report.getData().stream()
                        .map(DrillDownRow::getMetrics)
                        .collect(Collectors.toList()),
                everyItem(everyItem(NULL_ROW_MATCHER)));
        assertThat("Totals занулён", report.getTotals(), everyItem(NULL_ROW_MATCHER));
    }

    @After
    public void teardown() {
        resetCurrentLayer();
    }
}
