package ru.yandex.autotests.metrika.appmetrica.tests.ft.reporting.invariant;

import com.google.common.collect.ImmutableList;
import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import org.apache.commons.lang3.StringUtils;
import org.hamcrest.Matcher;
import org.hamcrest.Matchers;
import org.junit.After;
import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.irt.testutils.rules.parameters.IgnoreParameters;
import ru.yandex.autotests.irt.testutils.rules.parameters.IgnoreParametersList;
import ru.yandex.autotests.irt.testutils.rules.parameters.ParametersIgnoreRule;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.StatV1DataBytimeGETSchema;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.StatV1DataDrilldownGETSchema;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.StatV1DataGETSchema;
import ru.yandex.autotests.metrika.appmetrica.core.ParallelizedParameterized;
import ru.yandex.autotests.metrika.appmetrica.data.Users;
import ru.yandex.autotests.metrika.appmetrica.matchers.B2BMatchers;
import ru.yandex.autotests.metrika.appmetrica.parameters.*;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.autotests.metrika.appmetrica.tests.b2b.misc.B2BParameters;
import ru.yandex.autotests.metrika.appmetrica.utils.ReportUtils;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.ArrayList;
import java.util.Collection;

import static java.util.Arrays.asList;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.*;
import static org.hamcrest.core.Every.everyItem;
import static org.hamcrest.core.IsAnything.anything;
import static ru.yandex.autotests.irt.testutils.allure.AllureUtils.addTestParameter;
import static ru.yandex.autotests.metrika.appmetrica.data.ParallellismUtils.resetCurrentLayer;
import static ru.yandex.autotests.metrika.appmetrica.data.ParallellismUtils.setCurrentLayerByApp;
import static ru.yandex.autotests.metrika.appmetrica.data.Tables.*;
import static ru.yandex.autotests.metrika.appmetrica.steps.UserSteps.assumeOnResponse;
import static ru.yandex.autotests.metrika.appmetrica.tests.b2b.misc.B2BParameters.DimensionsDomain.FILTERABLE_DIMENSIONS;

/**
 * Проверяем инварианты фильтрации
 */
@Features(Requirements.Feature.DATA)
@Stories(Requirements.Story.DIMENSIONS)
@Title("Инварианты фильтрации (инварианты)")
@RunWith(ParallelizedParameterized.class)
public class DimensionFilterInvariantTest {

    @Rule
    public ParametersIgnoreRule ignoreRule = new ParametersIgnoreRule();

    private static final UserSteps user = UserSteps.onTesting(Users.SUPER_LIMITED);

    private static final Gson GSON = new GsonBuilder().create();

    private String dimensionValue;
    private Double metricValue;
    private String filter;
    private String namespace;

    @Parameterized.Parameter()
    public String dimensionName;

    @Parameterized.Parameter(1)
    public String metricName;

    @Parameterized.Parameter(2)
    public FreeFormParameters tail;

    @Parameterized.Parameter(3)
    public String appId;

    @Parameterized.Parameters(name = "dimension={0}, metric={1}, app_id={3}")
    public static Collection<Object[]> createParameters() {
        return ImmutableList.<Object[]>builder()
                .addAll(B2BParameters.createDimensionsWithout(FILTERABLE_DIMENSIONS,
                        asList(PROFILES, DEVICES, SKADNETWORK_POSTBACKS)))
                .addAll(B2BParameters.createDimensionsForProfiles(FILTERABLE_DIMENSIONS))
                .build();
    }

    @IgnoreParameters.Tag(name = "Need dimension to filter")
    public static Collection<Object[]> ignoredAsNeedDimensionToFilter() {
        return ImmutableList.<Object[]>builder()
                // avgParams зависит от количества строк и не переживает array join (MOBMET-15410)
                // то есть tableWithFilterTest отваливался бы если бы перед фильтрацией мы бы убивали dimension
                // но для сравнения сегментов мы пока множественные array join разрешать не хотим
                .add(new Object[]{Matchers.containsString(":paramsLevel"), Matchers.endsWith("avgParams"), anything(), anything()})
                .add(new Object[]{Matchers.containsString(":paramsValue"), Matchers.endsWith("avgParams"), anything(), anything()})
                // тут totals из null превращается в 0 при аналогичных изменениях
                .add(new Object[]{Matchers.containsString(":operatingSystemMinorVersionInfo"), Matchers.endsWith("avgParams"), anything(), anything()})
                .build();
    }

    @Before
    public void setup() {
        setCurrentLayerByApp(Long.parseLong(tail.get("id")));
        IFormParameters params = FreeFormParameters.makeParameters()
                .append(tail)
                .append(new TableReportParameters().withLimit(1));
        StatV1DataGETSchema result = user.onReportSteps().getTableReport(params);

        assumeOnResponse(result);

        addTestParameter("Измерение", dimensionName);

        dimensionValue = ReportUtils.getTableDimensions(result).get(0).get(0);
        metricValue = ReportUtils.getTableMetrics(result).get(0).get(0);

        // Для формирования фильтра нужно имя dimension-а с подстановкой
        String dimensionNameWithParam = tail.get("dimensions");
        filter = ReportUtils.buildDimensionFilter(dimensionNameWithParam, dimensionValue);
        namespace = StringUtils.substringBeforeLast(dimensionName, ":") + ":";

        addTestParameter("Фильтр", filter);
    }

    @Test
    public void tableWithFilterTest() {
        IFormParameters params = FreeFormParameters.makeParameters()
                .append(tail)
                .append(new TableReportParameters().withDimension(new ArrayList<>()).withFilters(filter));
        StatV1DataGETSchema result = user.onReportSteps().getTableReport(params);

        assumeOnResponse(result);

        assertThat("ответ содержит одну строку", result.getData(), hasSize(1));

        assertThat("значение измерения равно заданному",
                ReportUtils.getTableDimensions(result).get(0),
                allOf(iterableWithSize(1), everyItem(equalTo(dimensionValue))));

        assertThat("значение метрики равно заданному",
                ReportUtils.getTableMetrics(result).get(0),
                allOf(iterableWithSize(1), everyItem(metricMatcher(metricValue))));
    }

    @Test
    public void drilldownWithFilterTest() {
        IFormParameters params = FreeFormParameters.makeParameters()
                .append(tail)
                .append(new DrillDownReportParameters().withFilters(filter));
        StatV1DataDrilldownGETSchema result = user.onReportSteps().getDrillDownReport(params);

        assumeOnResponse(result);

        assertThat("ответ содержит одну строку", result.getData(), hasSize(1));

        assertThat("значение измерения в равно заданному", ReportUtils.getDrilldownDimensions(result),
                allOf(iterableWithSize(1), everyItem(equalTo(dimensionValue))));

        assertThat("значение метрики равно заданному",
                ReportUtils.getDrilldownMetrics(result).get(0),
                allOf(iterableWithSize(1), everyItem(metricMatcher(metricValue))));
    }

    @Test
    public void bytimeWithFilterTest() {
        IFormParameters params = FreeFormParameters.makeParameters()
                .append(tail)
                .append(new BytimeReportParameters().withFilters(filter).withGroup(GroupEnum.ALL));
        StatV1DataBytimeGETSchema result = user.onReportSteps().getByTimeReport(params);

        assumeOnResponse(result);

        assertThat("ответ содержит одну строку", result.getData(), hasSize(1));

        assertThat("значение измерения в равно заданному", ReportUtils.getBytimeDimensions(result).get(0),
                both(Matchers.<String>iterableWithSize(1)).and(everyItem(equalTo(dimensionValue))));

        assertThat("значение метрики равно заданному",
                ReportUtils.getBytimeMetrics(result).get(0).get(0),
                allOf(iterableWithSize(1), everyItem(metricMatcher(metricValue))));
    }

    @Test
    @IgnoreParametersList({
            @IgnoreParameters(reason = "Need dimension to filter", tag = "Need dimension to filter")
    })
    public void segmentComparisonTableTest() {
        IFormParameters params = FreeFormParameters.makeParameters()
                .append(tail)
                .append(new TableReportParameters().withDimension(namespace + "segment"))
                .append("segments", GSON.toJson(ImmutableList.of(filter)));
        StatV1DataGETSchema result = user.onReportSteps().getTableReport(params);

        assumeOnResponse(result);

        assertThat("ответ содержит одну строку", result.getData(), hasSize(1));

        assertThat("значение измерения равно заданному",
                ReportUtils.getTableDimensions(result).get(0),
                allOf(iterableWithSize(1), everyItem(equalTo("1"))));

        assertThat("значение метрики равно заданному",
                ReportUtils.getTableMetrics(result).get(0),
                allOf(iterableWithSize(1), everyItem(metricMatcher(metricValue))));

        // потому что include_undefined='false'
        assertThat("значение totals метрики равно заданному",
                ReportUtils.getTableMetricsTotals(result),
                allOf(iterableWithSize(1), everyItem(metricMatcher(metricValue))));
    }

    @After
    public void teardown() {
        resetCurrentLayer();
    }

    /**
     * Результаты фильтрации сравниваем приблизительно
     */
    private Matcher<Double> metricMatcher(Double metricValue) {
        return metricValue == null ? Matchers.nullValue(Double.class) : B2BMatchers.similarTo(metricValue);
    }
}
