package ru.yandex.autotests.metrika.tests.ft.report.metrika.dimensions.pairs;

import org.junit.Before;
import org.junit.Test;
import ru.yandex.autotests.metrika.beans.schemes.StatV1DataGETSchema;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.metadata.v1.ParameterValues;
import ru.yandex.autotests.metrika.data.parameters.report.v1.TableReportParameters;
import ru.yandex.autotests.metrika.steps.UserSteps;

import java.util.Collection;
import java.util.List;

import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.on;
import static java.util.Arrays.asList;
import static java.util.stream.Collectors.toList;
import static org.hamcrest.Matchers.*;
import static org.junit.runners.Parameterized.Parameter;
import static ru.yandex.autotests.metrika.commons.rules.IgnoreParameters.Tag;
import static ru.yandex.autotests.metrika.data.common.counters.Counter.ID;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.KVAZI_KAZINO;
import static ru.yandex.autotests.metrika.data.metadata.v1.ParameterValues.getDefaults;
import static ru.yandex.autotests.metrika.matchers.NoDuplicatesMatcher.hasNoDuplicates;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assumeThat;
import static ru.yandex.autotests.metrika.utils.Utils.replaceParameters;

/**
 * Created by konkov on 18.08.2014.
 */
public abstract class DimensionPairsBaseTest {

    protected static final Counter COUNTER = KVAZI_KAZINO;

    /**
     * Список наименований измерений для тестов парами по просмотрам
     * Источник - jkee@
     */
    protected static final List<String> HIT_DIMENSIONS = asList("ym:pv:URL", "ym:pv:URLParamName");
    /**
     * Список наименований измерений для тестов парами по визитам
     * Источник - jkee@
     */
    protected static final List<String> VISIT_DIMENSIONS = asList("ym:s:startURL", "ym:s:paramsLevel1");

    /**
     * user и counter инициализируются статически, т.к. они используются на этапе
     * формирования перечня параметров теста
     */
    protected static final UserSteps user = new UserSteps().withDefaultAccuracy();

    @Parameter()
    public List<String> dimensionNames;

    @Parameter(value = 1)
    public String metricName;

    protected StatV1DataGETSchema result;

    protected static ParameterValues getDefaultParameters() {
        return getDefaults(COUNTER);
    }

    @Before
    public void setup() {
        result = user.onReportSteps().getTableReportAndExpectSuccess(
                new TableReportParameters()
                        .withId(COUNTER.get(ID))
                        .withMetric(metricName)
                        .withDimensions(dimensionNames),
                getDefaultParameters().toFormParameters());
    }

    @Test
    public void checkDimensionsInQuery() {
        assumeThat("результат содержит исходный запрос", result,
                having(on(StatV1DataGETSchema.class).getQuery(), notNullValue()));

        List<String> expectedDimensionNames = dimensionNames.stream()
                .map(s -> replaceParameters(s, getDefaultParameters().toFormParameters()))
                .collect(toList());

        assertThat("результат содержит наименование измерений", result.getQuery().getDimensions(),
                equalTo(expectedDimensionNames));
    }

    @Test
    public void checkDimensionPairsUniqueness() {
        List<List<String>> dimensions = user.onResultSteps().getDimensions(result);

        assertThat("результат не содержит неуникальных пар измерений", dimensions, hasNoDuplicates());
    }

    @Tag(name = "*Name")
    public static Collection<Object[]> ignoreParameters() {
        return asList(new Object[][]{
                {contains(anything(), endsWith("Name")), anything()}
        });
    }
}
