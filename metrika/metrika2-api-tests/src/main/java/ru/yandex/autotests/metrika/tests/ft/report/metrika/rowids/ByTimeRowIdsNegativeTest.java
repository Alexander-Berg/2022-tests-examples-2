package ru.yandex.autotests.metrika.tests.ft.report.metrika.rowids;

import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.parameters.report.v1.BytimeReportParameters;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import static com.google.common.collect.ImmutableList.of;
import static java.util.Arrays.asList;
import static ru.yandex.autotests.metrika.data.common.counters.Counter.ID;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.YANDEX_METRIKA_2_0;
import static ru.yandex.autotests.metrika.errors.ReportError.VALUE_NOT_SUPPORTED_FOR_DIMENSION;

/**
 * Created by okunev on 30.10.2014.
 */
@Features(Requirements.Feature.REPORT)
@Stories({Requirements.Story.Report.Type.BYTIME, Requirements.Story.Report.Parameter.ROW_IDS})
@Title("Отчет 'по времени': выбор строк: проверка получения строки по некорректному id")
@RunWith(Parameterized.class)
public class ByTimeRowIdsNegativeTest {

    private static final String METRIC = "ym:s:users";

    private static UserSteps user = new UserSteps().withDefaultAccuracy();
    private static final Counter counter = YANDEX_METRIKA_2_0;

    @Parameterized.Parameter()
    public String dimension;

    @Parameterized.Parameter(1)
    public String value;

    @Parameterized.Parameters(name = "dimension: {0}, id: {1}")
    public static Collection<Object[]> createParameters() {
        return asList(new Object[][]{
                {"ym:s:searchEngineRoot", "abc"},
                {"ym:s:gender", "7"},
                {"ym:s:lastDirectPlatform", "zag3"},
                {"ym:s:pageViews", null},
        });
    }

    @Test
    public void bytimeRowidsCheckIncompatibleId() {
        List<String> row = new ArrayList<>();
        row.add(value);

        user.onReportSteps().getBytimeReportAndExpectError(
                VALUE_NOT_SUPPORTED_FOR_DIMENSION,
                new BytimeReportParameters()
                        .withId(counter.get(ID))
                        .withMetric(METRIC)
                        .withDimension(dimension)
                        .withRowIds(of(row)));
    }

}
