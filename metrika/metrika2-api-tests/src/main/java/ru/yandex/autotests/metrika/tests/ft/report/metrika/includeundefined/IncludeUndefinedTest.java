package ru.yandex.autotests.metrika.tests.ft.report.metrika.includeundefined;

import org.apache.commons.lang3.tuple.Pair;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.commons.junitparams.MultiplicationBuilder;
import ru.yandex.autotests.metrika.commons.junitparams.combinatorial.CombinatorialBuilder;
import ru.yandex.autotests.metrika.converters.DimensionToHumanReadableStringMapper;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.common.counters.Counters;
import ru.yandex.autotests.metrika.data.common.handles.RequestType;
import ru.yandex.autotests.metrika.data.metadata.v1.ParameterValues;
import ru.yandex.autotests.metrika.data.metadata.v1.enums.ParametrizationTypeEnum;
import ru.yandex.autotests.metrika.data.metadata.v1.enums.TableEnum;
import ru.yandex.autotests.metrika.data.parameters.FreeFormParameters;
import ru.yandex.autotests.metrika.data.parameters.management.v1.ClientsParameters;
import ru.yandex.autotests.metrika.data.parameters.report.v1.CommonReportParameters;
import ru.yandex.autotests.metrika.reportwrappers.Report;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;
import java.util.List;
import java.util.function.BiFunction;
import java.util.function.Function;
import java.util.stream.Stream;

import static com.google.common.collect.ImmutableList.of;
import static org.hamcrest.Matchers.*;
import static ru.yandex.autotests.metrika.data.common.handles.RequestTypes.*;
import static ru.yandex.autotests.metrika.data.metadata.v1.enums.ParametrizationTypeEnum.ATTRIBUTION;
import static ru.yandex.autotests.metrika.data.metadata.v1.enums.ParametrizationTypeEnum.GROUP;
import static ru.yandex.autotests.metrika.data.parameters.FreeFormParameters.makeParameters;
import static ru.yandex.autotests.metrika.data.parameters.ParametersUtils.comparisonDateParameters;
import static ru.yandex.autotests.metrika.data.parameters.ParametersUtils.dateParameters;
import static ru.yandex.autotests.metrika.data.parameters.management.v1.DelegateParameters.ulogin;
import static ru.yandex.autotests.metrika.data.report.v1.enums.GroupEnum.HOUR;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.any;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.*;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assumeThat;
import static ru.yandex.metrika.segments.site.parametrization.Attribution.LAST;

@Features(Requirements.Feature.REPORT)
@Stories(Requirements.Story.Report.Parameter.INCLUDE_UNDEFINED)
@Title("Не определенные значения измерений")
@RunWith(Parameterized.class)
public class IncludeUndefinedTest {

    private static final UserSteps user = new UserSteps().withDefaultAccuracy();
    private static final Counter COUNTER = Counters.SHATURA_COM;

    private static final String VISITS_METRIC_NAME = "ym:s:visits";
    private static final String ADVERTISING_METRIC_NAME = "ym:ad:visits";
    private static final String DOWNLOADS_METRIC_NAME = "ym:dl:users";
    private static final String SHARE_SERVICES_METRIC_NAME = "ym:sh:users";
    private static final String EXTERNAL_LINKS_METRIC_NAME = "ym:el:users";
    private static final String HITS_METRIC_NAME = "ym:pv:users";
    private static final String SITE_SPEED_METRIC_NAME = "ym:sp:users";

    private static final String START_DATE = "2016-01-31";
    private static final String END_DATE = "2016-01-31";

    @Parameterized.Parameter()
    public RequestType<?> requestType;

    @Parameterized.Parameter(1)
    public BiFunction<String, String, IFormParameters> dateParameters;

    @Parameterized.Parameter(2)
    public String dimension;

    @Parameterized.Parameter(3)
    public IncludeUndefinedTest.Holder holder;

    static class Holder {
        private FreeFormParameters tail = makeParameters();
        private String dimensionName;
        private String date1;
        private String date2;

        public FreeFormParameters getTail() {
            return tail;
        }

        public String getDimensionName() {
            return dimensionName;
        }

        public void setDimensionName(String dimensionName) {
            this.dimensionName = dimensionName;
        }

        public String getDate1() {
            return date1;
        }

        public IncludeUndefinedTest.Holder setDate1(String date1) {
            this.date1 = date1;
            return this;
        }

        public String getDate2() {
            return date2;
        }

        public IncludeUndefinedTest.Holder setDate2(String date2) {
            this.date2 = date2;
            return this;
        }

        public IncludeUndefinedTest.Holder withDate1(final String date1) {
            this.date1 = date1;
            return this;
        }

        public IncludeUndefinedTest.Holder withDate2(final String date2) {
            this.date2 = date2;
            return this;
        }
    }

    @Parameterized.Parameters(name = "{0}, {2}")
    public static Collection<Object[]> createParameters() {
        return CombinatorialBuilder.builder()
                .vectorValues(
                        of(TABLE, dateParameters()),
                        of(DRILLDOWN, dateParameters()),
                        of(COMPARISON, comparisonDateParameters()),
                        of(COMPARISON_DRILLDOWN, comparisonDateParameters()),
                        of(BY_TIME, dateParameters()))
                .vectorValues(MultiplicationBuilder.<String, String, Holder>builder(
                        user.onMetadataSteps().getDimensionsRaw(dimension(favorite()
                                .and(matches(not(containsString("datePeriod"))))
                                .and(matches(not(containsString("paramsLevel"))))
                                .and(matches(not(containsString("DirectBanner")))))), Holder::new)
                        .apply(any(),
                                (d, h) -> {
                                    h.getTail().append(
                                            new CommonReportParameters()
                                                    .withMetric(VISITS_METRIC_NAME)
                                                    .withId(COUNTER)
                                                    .withAccuracy("0.01"));
                                    h.setDate1(START_DATE);
                                    h.setDate2(END_DATE);
                                    return Stream.of(Pair.of(d, h));
                                })
                        .apply(table(TableEnum.ADVERTISING),
                                (d, h) -> {
                                    h.getTail().append(
                                            new CommonReportParameters()
                                                    .withMetric(ADVERTISING_METRIC_NAME)
                                                    .withDirectClientLogins(
                                                            user.onManagementSteps().onClientSteps().getClientLogins(
                                                                    new ClientsParameters()
                                                                            .withCounters(COUNTER)
                                                                            .withDate1(START_DATE)
                                                                            .withDate2(END_DATE),
                                                                    ulogin(COUNTER))));
                                    return Stream.of(Pair.of(d, h));
                                })
                        .apply(table(TableEnum.DOWNLOADS),
                                (d, h) -> {
                                    h.getTail().append(
                                            new CommonReportParameters()
                                                    .withMetric(DOWNLOADS_METRIC_NAME));
                                    return Stream.of(Pair.of(d, h));
                                })
                        .apply(table(TableEnum.SHARE_SERVICES),
                                (d, h) -> {
                                    h.getTail().append(
                                            new CommonReportParameters()
                                                    .withMetric(SHARE_SERVICES_METRIC_NAME));
                                    return Stream.of(Pair.of(d, h));
                                })
                        .apply(table(TableEnum.EXTERNAL_LINKS),
                                (d, h) -> {
                                    h.getTail().append(
                                            new CommonReportParameters()
                                                    .withMetric(EXTERNAL_LINKS_METRIC_NAME));
                                    return Stream.of(Pair.of(d, h));
                                })
                        .apply(table(TableEnum.HITS),
                                (d, h) -> {
                                    h.getTail().append(
                                            new CommonReportParameters()
                                                    .withMetric(HITS_METRIC_NAME));
                                    return Stream.of(Pair.of(d, h));
                                })
                        .apply(table(TableEnum.SITE_SPEED),
                                (d, h) -> {
                                    h.getTail().append(
                                            new CommonReportParameters()
                                                    .withMetric(SITE_SPEED_METRIC_NAME));
                                    return Stream.of(Pair.of(d, h));
                                })
                        .apply(parameterized(ATTRIBUTION),
                                (d, h) -> {
                                    d = new ParameterValues()
                                            .append(ParametrizationTypeEnum.ATTRIBUTION, String.valueOf(LAST))
                                            .substitute(d);
                                    return Stream.of(Pair.of(d, h));
                                })
                        .apply(parameterized(GROUP),
                                (d, h) -> {
                                    d = new ParameterValues()
                                            .append(ParametrizationTypeEnum.GROUP, String.valueOf(HOUR))
                                            .substitute(d);
                                    return Stream.of(Pair.of(d, h));
                                })
                        .apply(matches(equalTo("ym:sh:gender")),
                                (d, h) -> {
                                    h.setDate1("2015-07-10");
                                    h.setDate2("2015-07-30");
                                    return Stream.of(Pair.of(d, h));
                                })
                        .buildVectorValues(Function.identity()))
                .build();
    }

    @Test
    public void checkIncludeUndefined() {
        Report result = user.onReportSteps().getReportAndExpectSuccess(
                requestType,
                new CommonReportParameters()
                        .withDimension(dimension)
                        .withIncludeUndefined(true),
                holder.getTail(),
                dateParameters.apply(holder.getDate1(), holder.getDate2()));

        List<String> dimensionValues = result.getDimension(dimension);

        assumeThat("значения измерений содержат неопределенное значение", dimensionValues,
                hasItem(DimensionToHumanReadableStringMapper.NULL_RU));
    }

    @Test
    public void checkNotIncludeUndefinedExplicit() {
        Report result = user.onReportSteps().getReportAndExpectSuccess(
                requestType,
                new CommonReportParameters()
                        .withDimension(dimension)
                        .withIncludeUndefined(false),
                holder.getTail(),
                dateParameters.apply(holder.getDate1(), holder.getDate2()));

        List<String> dimensionValues = result.getDimension(dimension);

        assertThat("значения измерений не содержат неопределенных значений", dimensionValues,
                not(hasItem(DimensionToHumanReadableStringMapper.NULL_RU)));
    }

    @Test
    public void checkNotIncludeUndefinedImplicit() {
        Report result = user.onReportSteps().getReportAndExpectSuccess(
                requestType,
                new CommonReportParameters()
                        .withDimension(dimension),
                holder.getTail(),
                dateParameters.apply(holder.getDate1(), holder.getDate2()));

        List<String> dimensionValues = result.getDimension(dimension);

        assertThat("значения измерений не содержат неопределенных значений", dimensionValues,
                not(hasItem(DimensionToHumanReadableStringMapper.NULL_RU)));
    }
}
