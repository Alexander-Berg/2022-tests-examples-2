package ru.yandex.autotests.metrika.tests.ft.report.legacy;

import org.apache.commons.lang3.StringUtils;
import org.junit.Before;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.common.counters.Counters;
import ru.yandex.autotests.metrika.data.metadata.legacy.LegacyPresetWrapper;
import ru.yandex.autotests.metrika.data.parameters.FreeFormParameters;
import ru.yandex.autotests.metrika.data.parameters.report.v1.TableReportParameters;
import ru.yandex.autotests.metrika.commons.rules.IgnoreParameters;
import ru.yandex.autotests.metrika.steps.UserSteps;

import java.util.Collection;
import java.util.List;

import static java.util.Arrays.asList;
import static org.apache.commons.lang3.StringUtils.EMPTY;
import static ru.yandex.autotests.metrika.data.common.counters.Counter.ID;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.SENDFLOWERS_RU;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.SHATURA_COM;
import static ru.yandex.autotests.metrika.data.parameters.report.v1.GoalIdParameters.goalId;
import static ru.yandex.autotests.metrika.sort.SortBuilder.sort;

/**
 * Created by konkov on 02.12.2014.
 */
public class LegacyReportBaseTest {

    /**
     * user инициализируется статически, т.к. он используется на этапе
     * формирования перечня параметров теста
     */
    protected static final UserSteps user = new UserSteps();

    protected static final List<Counter> counters = asList(
            SENDFLOWERS_RU,
            Counters.SHATURA_COM);

    private static final String START_DATE = "2015-02-16";
    private static final String END_DATE = "2015-03-16";

    @Parameterized.Parameter(value = 0)
    public LegacyPresetWrapper preset;

    @Parameterized.Parameter(value = 1)
    public Counter counter;

    @Parameterized.Parameter(value = 2)
    public String goalId;

    protected IFormParameters getReportParameters() {
        IFormParameters reportParameters = new TableReportParameters()
                .withId(counter.get(ID))
                .withPreset(preset.getPreset().getName())
                .withDate1(START_DATE)
                .withDate2(END_DATE)
                .withSort(sort().by(preset.getPreset().getDimensions().get(0)).build());

        if (StringUtils.isNotEmpty(goalId)) {
            reportParameters = new FreeFormParameters().append(goalId(goalId), reportParameters);
        }

        return reportParameters;
    }

    @Before
    public void setup() {
        user.onLegacyMetadataSteps().attachPreset(preset);
    }

    @IgnoreParameters.Tag(name = "METR-23070")
    public static Collection<Object[]> ignoreParametersMetr23070() {
        return asList(new Object[][]{
                {"external_links", SENDFLOWERS_RU, EMPTY},
                {"external_links", SHATURA_COM, EMPTY},
                {"downloads", SENDFLOWERS_RU, EMPTY},
                {"downloads", SHATURA_COM, EMPTY}
        });
    }
}
