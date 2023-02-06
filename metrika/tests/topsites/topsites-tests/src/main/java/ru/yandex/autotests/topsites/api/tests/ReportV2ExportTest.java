package ru.yandex.autotests.topsites.api.tests;

import org.junit.Test;
import ru.yandex.autotests.metrika.commons.schemas.CsvResponseSchema;
import ru.yandex.autotests.metrika.commons.schemas.XlsxResponseSchema;
import ru.yandex.autotests.topsites.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Title;

import static org.hamcrest.Matchers.greaterThan;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.topsites.api.TopSitesFeatures.REPORT_V2;

@Features(REPORT_V2)
@Title("Экспорт отчета v2")
public class ReportV2ExportTest {

    private static final UserSteps user = new UserSteps();

    @Test
    @Title("Отчет v2 в формате CSV")
    public void testCsv() {
        CsvResponseSchema response = user.onTopSitesSteps().getReport2Csv();
        assertThat("вернулся непустой отчет", response.getData().size(), greaterThan(0));
    }

    @Test
    @Title("Отчет v2 в формате XLSX")
    public void testXlsx() {
        XlsxResponseSchema response = user.onTopSitesSteps().getReport2Xlsx();
        assertThat("вернулся непустой отчет", response.getData().getPhysicalNumberOfRows(), greaterThan(0));
    }
}
