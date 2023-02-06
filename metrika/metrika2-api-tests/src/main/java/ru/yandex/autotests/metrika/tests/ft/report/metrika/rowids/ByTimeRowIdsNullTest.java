package ru.yandex.autotests.metrika.tests.ft.report.metrika.rowids;

import org.junit.Test;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.parameters.report.v1.BytimeReportParameters;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Issue;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static java.util.Arrays.asList;
import static ru.yandex.autotests.metrika.data.common.counters.Counter.ID;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.WIKIMART_RU;
import static ru.yandex.autotests.metrika.data.report.v1.enums.GroupEnum.DAY;

/**
 * Created by konkov on 14.10.2015.
 */
@Features(Requirements.Feature.REPORT)
@Stories({Requirements.Story.Report.Type.BYTIME, Requirements.Story.Report.Parameter.ROW_IDS})
@Title("Отчет 'по времени': выбор строк: проверка получения строки по id null")
@Issue("METR-17625")
public class ByTimeRowIdsNullTest {
    private static final String METRIC = "ym:s:visits";
    private static final String DIMENSION = "ym:s:gender";
    private static final String START_DATE = "2015-09-01";
    private static final String END_DATE = "2015-09-10";

    private static final Counter COUNTER = WIKIMART_RU;

    private UserSteps user = new UserSteps().withDefaultAccuracy();

    @Test
    public void nullRowIdsTest() {
        user.onReportSteps().getBytimeReportAndExpectSuccess(
                new BytimeReportParameters()
                        .withId(COUNTER.get(ID))
                        .withRowIds(asList(asList(new String[]{null})))
                        .withDimension(DIMENSION)
                        .withMetric(METRIC)
                        .withDate1(START_DATE)
                        .withDate2(END_DATE)
                        .withGroup(DAY));
    }
}
