package ru.yandex.autotests.metrika.tests.b2b.metrika.ids;

import org.apache.commons.lang3.tuple.Pair;
import org.junit.Before;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.commons.junitparams.MultiplicationBuilder;
import ru.yandex.autotests.metrika.commons.junitparams.combinatorial.CombinatorialBuilder;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.common.handles.RequestType;
import ru.yandex.autotests.metrika.data.metadata.v1.enums.TableEnum;
import ru.yandex.autotests.metrika.data.parameters.FreeFormParameters;
import ru.yandex.autotests.metrika.data.parameters.report.v1.CommonReportParameters;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.autotests.metrika.tests.b2b.BaseB2bTest;
import ru.yandex.metrika.api.constructor.response.DimensionMetaExternal;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;
import java.util.function.BiFunction;
import java.util.stream.Stream;

import static com.google.common.collect.ImmutableList.of;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.*;
import static ru.yandex.autotests.metrika.data.common.handles.RequestTypes.*;
import static ru.yandex.autotests.metrika.data.metadata.v1.enums.TableEnum.ADVERTISING;
import static ru.yandex.autotests.metrika.data.metadata.v1.enums.TableEnum.USER_PARAM;
import static ru.yandex.autotests.metrika.data.parameters.FreeFormParameters.makeParameters;
import static ru.yandex.autotests.metrika.data.parameters.ParametersUtils.comparisonDateParameters;
import static ru.yandex.autotests.metrika.data.parameters.ParametersUtils.dateParameters;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.*;

/**
 * Created by sourx on 07.11.17.
 */
@Features(Requirements.Feature.DATA)
@Stories(Requirements.Story.Report.Parameter.DIMENSIONS)
@Title("B2B - запросы по измерениям для групп счетчиков")
public class B2bIdsDimensionsTest extends BaseB2bTest {
    private static final UserSteps user = new UserSteps();

    private static final Collection<Counter> COUNTERS = of(SENDFLOWERS_RU,
            SHATURA_COM,
            GENVIC_RU);

    private static final String VISITS_METRIC_NAME = "ym:s:affinityIndexInterests";
    private static final String HITS_METRIC_NAME = "ym:pv:blockedPercentage";
    private static final String EXTERNAL_LINKS_METRIC_NAME = "ym:el:links";
    private static final String DOWNLOADS_METRIC_NAME = "ym:dl:downloads";
    private static final String SHARE_SERVICES_METRIC_NAME = "ym:sh:users";
    private static final String SITE_SPEED_METRIC_NAME = "ym:sp:pageviewsPerDay";

    private static final String START_DATE = "2017-07-23";
    private static final String END_DATE = "2017-07-23";
    private static final String ACCURACY = "1";

    @Parameterized.Parameter()
    public RequestType<?> requestTypes;

    @Parameterized.Parameter(1)
    public BiFunction<String, String, IFormParameters> dateParameters;

    @Parameterized.Parameter(2)
    public String dimension;

    @Parameterized.Parameter(3)
    public Holder holder;

    static class Holder {
        private FreeFormParameters tail = makeParameters();
        private String metricName;

        public FreeFormParameters getTail() {
            return tail;
        }

        public String getMetricName() {
            return metricName;
        }

        public void setMetricName(String metricName) {
            this.metricName = metricName;
        }
    }

    @Parameterized.Parameters(name = "{0}, {2}")
    public static Collection<Object[]> createParameters() {
        return CombinatorialBuilder.builder()
                .vectorValues(
                        of(GLOBAL_TABLE, dateParameters()),
                        of(GLOBAL_BY_TIME, dateParameters()),
                        of(GLOBAL_DRILLDOWN, dateParameters()),
                        of(GLOBAL_COMPARISON, comparisonDateParameters()),
                        of(GLOBAL_COMPARISON_DRILLDOWN, comparisonDateParameters()))
                .vectorValues(MultiplicationBuilder.<DimensionMetaExternal, String, B2bIdsDimensionsTest.Holder>builder(
                        user.onMetadataSteps().getDimensionsMeta(dimension(favorite()
                                .and(table(ADVERTISING).negate())
                                .and(table(USER_PARAM).negate()))), Holder::new)
                        .apply(dimension(table(TableEnum.VISITS)),
                                (m, h) -> {
                                    h.setMetricName(VISITS_METRIC_NAME);
                                    return Stream.of(Pair.of(m, h));
                                })
                        .apply(dimension(table(TableEnum.HITS)),
                                (m, h) -> {
                                    h.setMetricName(HITS_METRIC_NAME);
                                    return Stream.of(Pair.of(m, h));
                                })
                        .apply(dimension(table(TableEnum.EXTERNAL_LINKS)),
                                (m, h) -> {
                                    h.setMetricName(EXTERNAL_LINKS_METRIC_NAME);
                                    return Stream.of(Pair.of(m, h));
                                })
                        .apply(dimension(table(TableEnum.DOWNLOADS)),
                                (m, h) -> {
                                    h.setMetricName(DOWNLOADS_METRIC_NAME);
                                    return Stream.of(Pair.of(m, h));
                                })
                        .apply(dimension(table(TableEnum.SHARE_SERVICES)),
                                (m, h) -> {
                                    h.setMetricName(SHARE_SERVICES_METRIC_NAME);
                                    return Stream.of(Pair.of(m, h));
                                })
                        .apply(dimension(table(TableEnum.SITE_SPEED)),
                                (m, h) -> {
                                    h.setMetricName(SITE_SPEED_METRIC_NAME);
                                    return Stream.of(Pair.of(m, h));
                                })
                        .buildVectorValues(DimensionMetaExternal::getDim))
                .build();
    }

    @Before
    public void setup() {
        requestType = requestTypes;
        reportParameters = holder.getTail().append(
                new CommonReportParameters()
                        .withIds(COUNTERS)
                        .withMetric(holder.getMetricName())
                        .withDimension(dimension)
                        .withAccuracy(ACCURACY))
                .append(
                        dateParameters.apply(START_DATE, END_DATE));
    }
}
