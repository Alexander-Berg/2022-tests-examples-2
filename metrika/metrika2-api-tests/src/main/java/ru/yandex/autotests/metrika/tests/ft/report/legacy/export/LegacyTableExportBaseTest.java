package ru.yandex.autotests.metrika.tests.ft.report.legacy.export;

import org.hamcrest.Matchers;
import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.commons.rules.IgnoreParameters;
import ru.yandex.autotests.metrika.commons.rules.IgnoreParametersList;
import ru.yandex.autotests.metrika.commons.rules.ParametersIgnoreRule;
import ru.yandex.autotests.metrika.tests.ft.report.legacy.LegacyReportBaseTest;

import java.util.Collection;
import java.util.List;

import static java.util.Arrays.asList;
import static org.apache.commons.lang3.StringUtils.EMPTY;
import static org.hamcrest.Matchers.*;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.SENDFLOWERS_RU;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.SHATURA_COM;
import static ru.yandex.autotests.metrika.matchers.TwoDimensionalArrayMatcher.everyRowStartsWithRowOf;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

/**
 * Created by konkov on 22.07.2015.
 */
public abstract class LegacyTableExportBaseTest extends LegacyReportBaseTest {

    private List<List<String>> expectedRows;
    private List<List<String>> actualRows;

    @Parameterized.Parameters(name = "{0} {1} {2}")
    public static Collection<Object[]> createParameters() {
        return user.onLegacyMetadataSteps().getPresetCounterGoalParameters(counters);
    }

    protected abstract List<List<String>> getDataFromExportedReport();

    protected abstract List<List<String>> getDataFromReport();

    @Before
    public void setup() {
        super.setup();
        expectedRows = getDataFromReport();
        actualRows = getDataFromExportedReport();
    }

    @Test
    public void exportNonJsonCheckSize() {
        int dimensionsAndMetricsCount = preset.getPreset().getDimensions().size() +
                preset.getPreset().getMetrics().size();

        assertThat("результат содержит одинаковое с json количество элементов", actualRows,
                is(both(Matchers.<Iterable<Iterable>>iterableWithSize(expectedRows.size()))
                        .and(everyItem(is(Matchers.<Iterable>iterableWithSize(dimensionsAndMetricsCount))))));
    }

    @Test
    public void exportNonJsonCheckValues() {
        assertThat("результат содержит одинаковые с json измерения", actualRows,
                everyRowStartsWithRowOf(expectedRows));
    }
}
