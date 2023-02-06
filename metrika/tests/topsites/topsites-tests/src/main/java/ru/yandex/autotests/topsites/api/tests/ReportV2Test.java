package ru.yandex.autotests.topsites.api.tests;

import org.junit.Before;
import org.junit.Test;
import ru.yandex.autotests.topsites.data.parameters.report.TopSitesReportParameters;
import ru.yandex.autotests.topsites.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Title;
import ru.yandex.topsites.GlobalTopsitesReport2GETSchema;

import static org.hamcrest.Matchers.*;
import static ru.yandex.autotests.topsites.core.TopSitesMatchers.reportDataSortMatcher;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.topsites.api.TopSitesFeatures.REPORT_V2;

@Features(REPORT_V2)
@Title("Отчет v2")
public class ReportV2Test {

    private static final UserSteps user = new UserSteps();

    private GlobalTopsitesReport2GETSchema report2;

    @Before
    public void setup() {
        report2 = user.onTopSitesSteps().getReport2();
    }

    @Test
    @Title("Текущий топ v2 вернул snapshotId")
    public void currentGlobalTopHasSnapshotId() {
        assertThat("snapshotId существует", report2.getSnapshotId(), notNullValue());
    }

    @Test
    @Title("Текущий топ v2 содержит строки, сортированные по cryptaMau")
    public void currentGlobalTopIsSorted() {
        assertThat("вернулся сортированный по cryptaMau набор строк", report2.getData(),
                reportDataSortMatcher(report2.getData())
        );
    }

    @Test
    @Title("Текущий топ v2 содержит 10 строк")
    public void currentGlobalTopHasTenRecords() {
        assertThat("вернулось 10 строк", report2.getData(), iterableWithSize(10));
    }

    @Test
    @Title("limit работает v2")
    public void limit() {
        GlobalTopsitesReport2GETSchema reportWithLimit = user.onTopSitesSteps().getReport2(new TopSitesReportParameters().withLimit(17));
        assertThat("вернулось limit строк", reportWithLimit.getData(), iterableWithSize(17));
    }

    @Test
    @Title("offset работает v2")
    public void offset() {
        int offset = 9;
        GlobalTopsitesReport2GETSchema reportWithOffset = user.onTopSitesSteps()
                .getReport2(new TopSitesReportParameters().withOffset(offset).withSnapshotId(report2.getSnapshotId()));
        assertThat("строка по offset - 1 из запроса без offset равна первой строке из запроса с offset",
                reportWithOffset.getData().get(0), equalTo(report2.getData().get(offset - 1)));
    }
}
