package ru.yandex.autotests.metrika.tests.ft.report.metrika.filters.table;

import org.junit.Before;
import org.junit.Test;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.beans.schemes.StatV1DataGETSchema;
import ru.yandex.autotests.metrika.data.parameters.report.v1.TableReportParameters;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static org.hamcrest.Matchers.not;
import static ru.yandex.autotests.irt.testutils.beandiffer.BeanDifferMatcher.beanEquivalent;
import static ru.yandex.autotests.metrika.utils.AllureUtils.*;

@Features(Requirements.Feature.DATA)
@Stories({Requirements.Story.Report.MANUAL_SAMPLES, Requirements.Story.Report.Type.TABLE})
@Title("Фильтры: для метрик по currency с разными валютами")
public class CurrencyFilterTest {
    protected static final UserSteps userOnTest = new UserSteps().withDefaultAccuracy();


    @Test
    public void inlinedCurrencyWorks() {
        StatV1DataGETSchema usdRevenueFilterInlinedResponse = userOnTest.onReportSteps().getTableReportAndExpectSuccess(getBaseParams().withFilters("ym:s:purchase840Revenue > 100"));
        StatV1DataGETSchema usdRevenueFilterParamResponse = userOnTest.onReportSteps().getTableReportAndExpectSuccess(getBaseParams().withFilters("ym:s:purchase<currency>Revenue > 100").withCurrency("840"));

        assertThat("ответы с фильтром purchaseRevenue в usd в инлайн и через параметр совпадают",
                usdRevenueFilterInlinedResponse.getData(), beanEquivalent(usdRevenueFilterParamResponse.getData()));
    }

    @Test
    public void usdResponseDiffersFromRur() {
        StatV1DataGETSchema rurRevenueFilterResponse = userOnTest.onReportSteps().getTableReportAndExpectSuccess(getBaseParams().withFilters("ym:s:purchase643Revenue > 100"));
        StatV1DataGETSchema usdRevenueFilterResponse = userOnTest.onReportSteps().getTableReportAndExpectSuccess(getBaseParams().withFilters("ym:s:purchase840Revenue > 100"));

        assertThat("ответы с фильтром purchaseRevenue в usd и rur отличаются",
                rurRevenueFilterResponse.getData(), not(beanEquivalent(usdRevenueFilterResponse.getData())));
    }

    private TableReportParameters getBaseParams() {
        return new TableReportParameters()
                .withId(4315831L)
                .withDate1("2018-08-08")
                .withDate2("2018-08-08")
                .withDimension("ym:s:userID")
                .withMetric("ym:s:visits")
                .withSort("ym:s:userID")
                .withLimit(1);
    }
}
