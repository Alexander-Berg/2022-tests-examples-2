package ru.yandex.autotests.metrika.tests.ft.report.legacy.export;

import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.beans.schemes.StatV1DataCsvSchema;
import ru.yandex.autotests.metrika.beans.schemes.StatV1DataGETSchema;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.List;

/**
 * Created by konkov on 22.07.2015.
 */
@Features(Requirements.Feature.LEGACY)
@Stories({Requirements.Story.Report.Parameter.PRESET, Requirements.Story.Report.Type.TABLE})
@Title("Legacy отчет 'таблица': экспорт в CSV")
@RunWith(Parameterized.class)
public class LegacyTableExportCsvTest extends LegacyTableExportBaseTest {

    @Override
    protected List<List<String>> getDataFromReport() {
        StatV1DataGETSchema result = user.onLegacyReportSteps()
                .getTableReportAndExpectSuccess(getReportParameters());

        return user.onResultSteps().getDimensionsNameOnly(result);
    }

    @Override
    protected List<List<String>> getDataFromExportedReport() {
        StatV1DataCsvSchema resultCsv = user.onLegacyReportSteps()
                .getCsvReportAndExpectSuccess(getReportParameters());

        return user.onResultSteps().getDimensionsAndMetricsFromCsv(resultCsv);
    }
}
