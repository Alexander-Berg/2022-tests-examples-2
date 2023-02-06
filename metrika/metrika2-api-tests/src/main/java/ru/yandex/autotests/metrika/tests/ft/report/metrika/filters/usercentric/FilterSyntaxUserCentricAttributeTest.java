package ru.yandex.autotests.metrika.tests.ft.report.metrika.filters.usercentric;

import org.apache.commons.lang3.tuple.Pair;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.commons.junitparams.MultiplicationBuilder;
import ru.yandex.autotests.metrika.commons.junitparams.combinatorial.CombinatorialBuilder;
import ru.yandex.autotests.metrika.commons.rules.IgnoreParameters;
import ru.yandex.autotests.metrika.commons.rules.ParametersIgnoreRule;
import ru.yandex.autotests.metrika.data.common.DateConstants;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.common.handles.RequestType;
import ru.yandex.autotests.metrika.data.metadata.v1.enums.TableEnum;
import ru.yandex.autotests.metrika.data.parameters.FreeFormParameters;
import ru.yandex.autotests.metrika.data.parameters.management.v1.ClientsParameters;
import ru.yandex.autotests.metrika.data.parameters.report.v1.CommonReportParameters;
import ru.yandex.autotests.metrika.filters.Expression;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;
import java.util.function.BiFunction;
import java.util.function.Function;
import java.util.stream.Stream;

import static com.google.common.collect.ImmutableList.of;
import static java.util.Arrays.asList;
import static java.util.function.Function.identity;
import static org.hamcrest.Matchers.anything;
import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.autotests.metrika.data.common.counters.Counter.ID;
import static ru.yandex.autotests.metrika.data.common.counters.Counter.U_LOGIN;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.DARIA_MAIL_YANDEX_RU;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.IKEA_VSEM;
import static ru.yandex.autotests.metrika.data.common.handles.RequestTypes.*;
import static ru.yandex.autotests.metrika.data.parameters.FreeFormParameters.makeParameters;
import static ru.yandex.autotests.metrika.data.parameters.ParametersUtils.*;
import static ru.yandex.autotests.metrika.data.parameters.management.v1.DelegateParameters.ulogin;
import static ru.yandex.autotests.metrika.data.parameters.report.v1.CurrencyParameters.currency;
import static ru.yandex.autotests.metrika.filters.Relation.exists;
import static ru.yandex.autotests.metrika.filters.Term.dimension;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.*;
import static ru.yandex.autotests.metrika.steps.metadata.UserCentricMetadataSteps.Predicates.filterType;
import static ru.yandex.metrika.segments.core.meta.segment.UserFilterType.ATTR;

@Features(Requirements.Feature.REPORT)
@Stories({
        Requirements.Story.Report.Type.TABLE,
        Requirements.Story.Report.Parameter.FILTERS,
        Requirements.Story.USER_CENTRIC
})
@Title("Фильтры: user-centric сегментация по атрибутам")
@RunWith(Parameterized.class)
public class FilterSyntaxUserCentricAttributeTest {

    @Rule
    public ParametersIgnoreRule parametersIgnoreRule = new ParametersIgnoreRule();

    protected static final UserSteps user = new UserSteps().withDefaultAccuracy();

    private static final Counter COUNTER = DARIA_MAIL_YANDEX_RU;

    private static final String START_DATE = "2015-09-01";
    private static final String END_DATE = "2015-09-02";

    protected static final String SPECIAL_DATE = "2015-08-01";

    private static final Counter ADVERTISING_COUNTER = IKEA_VSEM;
    private static final String ADVERTISING_START_DATE = DateConstants.Advertising.START_DATE;
    private static final String ADVERTISING_END_DATE = DateConstants.Advertising.END_DATE;

    @Parameterized.Parameter()
    public RequestType<?> requestType;

    @Parameterized.Parameter(1)
    public BiFunction<String, String, IFormParameters> dateParameters;

    @Parameterized.Parameter(2)
    public Function<String, IFormParameters> filtersParameters;

    @Parameterized.Parameter(3)
    public static String attributeName;

    @Parameterized.Parameter(4)
    public String metricName;

    @Parameterized.Parameter(5)
    public Holder holder;

    private static final class Holder {
        private FreeFormParameters tail = makeParameters();
        private String date1;
        private String date2;
        private Counter counter;

        public FreeFormParameters getTail() {
            return tail;
        }

        public String getDate1() {
            return date1;
        }

        public String getDate2() {
            return date2;
        }

        public Counter getCounter() {
            return counter;
        }

        public void setDate1(String date1) {
            this.date1 = date1;
        }

        public void setDate2(String date2) {
            this.date2 = date2;
        }

        public void setCounter(Counter counter) {
            this.counter = counter;
        }

        public Holder withDate1(final String date1) {
            this.date1 = date1;
            return this;
        }

        public Holder withDate2(final String date2) {
            this.date2 = date2;
            return this;
        }

        public Holder withCounter(final Counter counter) {
            this.counter = counter;
            return this;
        }
    }

    @Parameterized.Parameters(name = "{0} атрибут {3}")
    public static Collection<Object[]> createParameters() {
        return CombinatorialBuilder.builder()
                .vectorValues(
                        of(BY_TIME, dateParameters(), filtersParameters()),
                        of(TABLE, dateParameters(), filtersParameters()),
                        of(DRILLDOWN, dateParameters(), filtersParameters()),
                        of(COMPARISON, comparisonDateParameters(), comparisonFiltersParameters()),
                        of(COMPARISON_DRILLDOWN, comparisonDateParameters(), comparisonFiltersParameters()))
                .values(user.onUserCentricMetadataSteps().getUserCentricAttributes(filterType(ATTR)).stream())
                .vectorValues(MultiplicationBuilder.<String, String, Holder>builder(
                        user.onMetadataSteps().getMetrics(favorite().and(syntaxUserCentric())), Holder::new)
                        .apply(any(),
                                (d, h) -> {
                                    h.setCounter(COUNTER);
                                    h.setDate1(START_DATE);
                                    h.setDate2(END_DATE);
                                    h.getTail().append(new CommonReportParameters().withAccuracy("0.1"));
                                    return Stream.of(Pair.of(d, h));
                                })
                        .apply(table(TableEnum.VISITS),
                                (m, h) -> {
                                    h.getTail().append(
                                            new CommonReportParameters()
                                                    .withDimension(user.onMetadataSteps()
                                                            .getDimensions(syntaxUserCentric().and(table(TableEnum.VISITS)))));
                                    return Stream.of(Pair.of(m, h));
                                })
                        .apply(table(TableEnum.HITS),
                                (m, h) -> {
                                    h.getTail().append(
                                            new CommonReportParameters()
                                                    .withDimension(user.onMetadataSteps()
                                                            .getDimensions(syntaxUserCentric().and(table(TableEnum.HITS)))));
                                    return Stream.of(Pair.of(m, h));
                                })
                        .apply(table(TableEnum.ADVERTISING),
                                (m, h) -> {
                                    h.setDate1(ADVERTISING_START_DATE);
                                    h.setDate2(ADVERTISING_END_DATE);
                                    h.setCounter(ADVERTISING_COUNTER);
                                    h.getTail().append(
                                            new CommonReportParameters()
                                                    .withDimension(user.onMetadataSteps()
                                                            .getDimensions(syntaxUserCentric().and(table(TableEnum.ADVERTISING))))
                                                    .withDirectClientLogins(
                                                            user.onManagementSteps().onClientSteps().getClientLogins(
                                                                    new ClientsParameters()
                                                                            .withCounters(ADVERTISING_COUNTER.get(ID))
                                                                            .withDate1(ADVERTISING_START_DATE)
                                                                            .withDate2(ADVERTISING_END_DATE),
                                                                    ulogin(ADVERTISING_COUNTER.get(U_LOGIN)))),
                                            currency("643"));
                                    return Stream.of(Pair.of(m, h));
                                })
                        .buildVectorValues(identity()))
                .build();
    }

    @Test
    public void checkSimpleFilter() {
        user.onReportSteps().getReportAndExpectSuccess(
                requestType,
                dateParameters.apply(holder.date1, holder.date2),
                filtersParameters.apply(dimension(attributeName).defined().build()),
                getReportParameters(),
                holder.getTail());
    }

    @Test
    @IgnoreParameters(reason = "METR-39416", tag = "ym:up:specialDefaultDate")
    public void checkSimpleFilterSpecialDefaultDate() {
        user.onReportSteps().getReportAndExpectSuccess(
                requestType,
                dateParameters.apply(holder.date1, holder.date2),
                filtersParameters.apply(dimension(attributeName).defined()
                        .and(getSpecialDateFilter()).build()),
                getReportParameters(),
                holder.getTail());
    }

    @Test
    public void checkQuantorFilter() {
        user.onReportSteps().getReportAndExpectSuccess(
                requestType,
                dateParameters.apply(holder.date1, holder.date2),
                filtersParameters.apply(exists(dimension(attributeName).defined()).build()),
                getReportParameters(),
                holder.getTail());
    }

    @Test
    @IgnoreParameters(reason = "METR-33949", tag = "CastException")
    @IgnoreParameters(reason = "METR-39416", tag = "ym:up:specialDefaultDate")
    public void checkQuantorFilterSpecialDefaultDate() {
        user.onReportSteps().getReportAndExpectSuccess(
                requestType,
                dateParameters.apply(holder.date1, holder.date2),
                filtersParameters.apply(exists(dimension(attributeName).defined()
                        .and(getSpecialDateFilter())).build()),
                getReportParameters(),
                holder.getTail());
    }

    @Test
    public void checkExtendedQuantorFilter() {
        String userId = user.onUserCentricMetadataSteps().getUserIdAttribute(attributeName);

        user.onReportSteps().getReportAndExpectSuccess(
                requestType,
                dateParameters.apply(holder.date1, holder.date2),
                filtersParameters.apply(exists(userId, dimension(attributeName).defined()).build()),
                getReportParameters(),
                holder.getTail());
    }

    @Test
    @IgnoreParameters(reason = "METR-39416", tag = "ym:up:specialDefaultDate")
    public void checkExtendedQuantorFilterSpecialDefaultDate() {
        String userId = user.onUserCentricMetadataSteps().getUserIdAttribute(attributeName);

        user.onReportSteps().getReportAndExpectSuccess(
                requestType,
                dateParameters.apply(holder.date1, holder.date2),
                filtersParameters.apply(exists(userId, dimension(attributeName).defined()
                        .and(getSpecialDateFilter())).build()),
                getReportParameters(),
                holder.getTail());
    }

    protected CommonReportParameters getReportParameters() {
        return new CommonReportParameters()
                .withId(holder.counter.get(ID))
                .withMetric(metricName);
    }

    private static Expression getSpecialDateFilter() {
        return dimension(user.onUserCentricMetadataSteps().getSpecialDefaultDateAttribute(attributeName))
                .equalTo(SPECIAL_DATE);
    }

    @IgnoreParameters.Tag(name = "CastException")
    public static Collection<Object[]> ignoreParametersMetr33949() {
        return asList(new Object[][]{
                {anything(), anything(), anything(), equalTo("ym:u:interest2d1"), anything(), anything()}
        });
    }

    @IgnoreParameters.Tag(name = "ym:up:specialDefaultDate")
    public static Collection<Object[]> ignoreParametersMetr39416() {
        return asList(new Object[][]{
                {anything(), anything(), anything(), equalTo("ym:up:paramsLevel1"), anything(), anything()}
        });
    }
}
