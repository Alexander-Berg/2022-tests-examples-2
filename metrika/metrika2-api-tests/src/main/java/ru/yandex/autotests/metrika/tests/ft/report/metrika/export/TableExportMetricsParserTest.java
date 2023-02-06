package ru.yandex.autotests.metrika.tests.ft.report.metrika.export;

import org.apache.commons.csv.CSVRecord;
import org.apache.commons.lang3.tuple.Pair;
import org.apache.poi.xssf.usermodel.XSSFSheet;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.junit.runners.Parameterized.Parameter;
import org.junit.runners.Parameterized.Parameters;
import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.beans.schemes.StatV1DataCsvSchema;
import ru.yandex.autotests.metrika.beans.schemes.StatV1DataGETSchema;
import ru.yandex.autotests.metrika.beans.schemes.StatV1DataXlsxSchema;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.common.counters.Counters;
import ru.yandex.autotests.metrika.data.parameters.FreeFormParameters;
import ru.yandex.autotests.metrika.data.parameters.report.v1.TableReportParameters;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;
import java.util.Collections;
import java.util.List;

import static java.util.Arrays.asList;
import static org.hamcrest.Matchers.empty;
import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.autotests.metrika.data.parameters.FreeFormParameters.makeParameters;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assumeThat;

@Features(Requirements.Feature.REPORT)
@Stories({
        Requirements.Story.Report.Type.TABLE,
        Requirements.Story.Report.Format.XLSX,
        Requirements.Story.Report.Format.CSV
})
@Title("Экспорт в xlsx и csv, проверка правильности парсинга метрик и составления заголовков")
@RunWith(Parameterized.class)
public class TableExportMetricsParserTest {
    private final Counter COUNTER = Counters.NOTIK;
    private final String START_DATE = "2016-05-20";
    private final String END_DATE = "2016-05-22";
    private final String DIMENSION = "ym:s:productName";

    @Parameter(0)
    public String metricName;
    @Parameter(1)
    public List<Pair<String, String>> otherParams;
    @Parameter(2)
    public String expectedHeader;
    @Parameter(3)
    public String dimension;

    protected UserSteps user;

    @Parameters(name = "Метрика {0}")
    public static Collection<Object[]> createParameters() {
        return asList(
                new Object[]{
                        "ym:s:goal<goal_id>productBaskets<currency>Price",
                        asList(Pair.of("goal_id", "201813"), Pair.of("currency", "643")),
                        "Стоимость добавленных в корзину товаров (Адреса магазинов), RUB",
                        "ym:s:productName",
                },
                new Object[]{
                        "ym:s:conversionRateGroup201813reaches",
                        Collections.emptyList(),
                        "Достижения цели (Адреса магазинов)",
                        "ym:s:productName",
                },
                new Object[]{
                        "ym:s:conversionRateGroup201813reaches",
                        asList(Pair.of("currency", "RUB")),
                        "Достижения цели (Адреса магазинов)",
                        "ym:s:productName",
                },
                new Object[]{
                        "ym:s:ecommerce<currency>Revenue",
                        asList(Pair.of("currency", "RUB")),
                        "Доход, RUB",
                        "ym:s:productName",
                },
                new Object[]{
                        "ym:ad:goal201813revenue",
                        asList(Pair.of("direct_client_logins", "sendflowers")),
                        "Доход (Адреса магазинов)",
                        "ym:ad:LASTDirectBanner",
                }
        );
    }

    @Before
    public void setup() {
        user = new UserSteps();
        StatV1DataGETSchema result = user.onReportSteps().getTableReportAndExpectSuccess(getReportParameters());

        assumeThat("отчет данных не содержит", result.getData(), empty());
    }

    @Test
    public void checkExportXlsx() {
        StatV1DataXlsxSchema result = user.onReportSteps().getXlsxReportAndExpectSuccess(getReportParameters());
        String metricName = getHeaderText(result.getData());
        assertThat("Наименование метрики в заголовке xls соответствует ожидаемому", metricName, equalTo(expectedHeader));
    }

    private String getHeaderText(XSSFSheet data) {
        return data.getRow(data.getLastRowNum()).getCell(1).getStringCellValue();
    }

    @Test
    public void checkExportCsv() {
        StatV1DataCsvSchema result = user.onReportSteps().getCsvReportAndExpectSuccess(getReportParameters());
        String metricName = getHeaderText(result.getData());
        assertThat("Наименование метрики в заголовке csv соответствует ожидаемому", metricName, equalTo(expectedHeader));
    }

    private String getHeaderText(List<CSVRecord> data) {
        return data.get(data.size() - 1).get(1);
    }

    private IFormParameters getReportParameters() {
        FreeFormParameters params = makeParameters().append(new TableReportParameters()
                .withId(COUNTER)
                .withDate1(START_DATE)
                .withDate2(END_DATE)
                .withDimension(dimension)
                .withMetric(metricName)
                .withFilters("ym:s:productName=='9000347234'")
                .withLang("ru"));
        for (Pair<String, String> additional : otherParams) {
            params.append(additional.getKey(), additional.getValue());
        }
        return params;
    }

}
