package ru.yandex.autotests.metrika.tests.ft.report.metrika.attribution;

import org.apache.commons.lang3.tuple.Pair;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.commons.junitparams.MultiplicationBuilder;
import ru.yandex.autotests.metrika.commons.junitparams.combinatorial.CombinatorialBuilder;
import ru.yandex.autotests.metrika.data.common.DateConstants;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.common.counters.Counters;
import ru.yandex.autotests.metrika.data.common.handles.RequestType;
import ru.yandex.autotests.metrika.data.metadata.v1.enums.ParametrizationTypeEnum;
import ru.yandex.autotests.metrika.data.metadata.v1.enums.TableEnum;
import ru.yandex.autotests.metrika.data.parameters.FreeFormParameters;
import ru.yandex.autotests.metrika.data.parameters.management.v1.ClientsParameters;
import ru.yandex.autotests.metrika.data.parameters.report.v1.CommonReportParameters;
import ru.yandex.autotests.metrika.data.parameters.report.v1.ParametrizationParameters;
import ru.yandex.autotests.metrika.reportwrappers.Report;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.segments.site.parametrization.Attribution;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;
import java.util.function.BiFunction;
import java.util.stream.Stream;

import static com.google.common.collect.ImmutableList.of;
import static java.util.function.Function.identity;
import static ru.yandex.autotests.metrika.data.common.counters.Counter.ID;
import static ru.yandex.autotests.metrika.data.common.counters.Counter.U_LOGIN;
import static ru.yandex.autotests.metrika.data.common.handles.RequestTypes.*;
import static ru.yandex.autotests.metrika.data.parameters.FreeFormParameters.makeParameters;
import static ru.yandex.autotests.metrika.data.parameters.ParametersUtils.comparisonDateParameters;
import static ru.yandex.autotests.metrika.data.parameters.ParametersUtils.dateParameters;
import static ru.yandex.autotests.metrika.data.parameters.management.v1.DelegateParameters.ulogin;
import static ru.yandex.autotests.metrika.data.parameters.report.v1.CurrencyParameters.currency;
import static ru.yandex.autotests.metrika.data.parameters.report.v1.GoalIdParameters.goalId;
import static ru.yandex.autotests.metrika.matchers.Matchers.attributionEqualTo;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.*;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;
import static ru.yandex.autotests.metrika.utils.Utils.getEnumListWithNull;

/**
 * Created by konkov on 18.08.2016.
 */
@Features(Requirements.Feature.REPORT)
@Stories(Requirements.Story.Report.ATTRIBUTION)
@Title("Атрибуция")
@RunWith(Parameterized.class)
public class AttributionTest {

    private static final UserSteps user = new UserSteps().withDefaultAccuracy();

    private static final Counter COUNTER = Counters.SENDFLOWERS_RU;
    private static final String START_DATE = "2015-03-11";
    private static final String END_DATE = "2015-03-11";

    private static final Counter ADVERTISING_COUNTER = Counters.SHATURA_COM;
    private static final String ADVERTISING_START_DATE = DateConstants.Advertising.START_DATE;
    //запрос за один день
    private static final String ADVERTISING_END_DATE = DateConstants.Advertising.START_DATE;

    private Report result;

    @Parameterized.Parameter()
    public RequestType<?> requestType;

    @Parameterized.Parameter(1)
    public BiFunction<String, String, IFormParameters> dateParameters;

    @Parameterized.Parameter(2)
    public Attribution attribution;

    @Parameterized.Parameter(3)
    public String dimensionName;

    @Parameterized.Parameter(4)
    public Holder holder;

    private static final class Holder {
        private FreeFormParameters tail = makeParameters();
        private String date1;
        private String date2;

        public FreeFormParameters getTail() {
            return tail;
        }

        public String getDate1() {
            return date1;
        }

        public void setDate1(String date1) {
            this.date1 = date1;
        }

        public String getDate2() {
            return date2;
        }

        public void setDate2(String date2) {
            this.date2 = date2;
        }

        public Holder withDate1(final String date1) {
            this.date1 = date1;
            return this;
        }

        public Holder withDate2(final String date2) {
            this.date2 = date2;
            return this;
        }
    }

    @Parameterized.Parameters(name = "{0}, {3} атрибуция: {2}")
    public static Collection<Object[]> createParameters() {
        return CombinatorialBuilder.builder()
                .vectorValues(
                        of(BY_TIME, dateParameters()),
                        of(TABLE, dateParameters()),
                        of(DRILLDOWN, dateParameters()),
                        of(COMPARISON, comparisonDateParameters()),
                        of(COMPARISON_DRILLDOWN, comparisonDateParameters()))
                .values(getEnumListWithNull(Attribution.class))
                .vectorValues(MultiplicationBuilder.<String, String, Holder>builder(
                        user.onMetadataSteps().getDimensions(
                                favorite().and(table(TableEnum.VISITS).or(table(TableEnum.ADVERTISING))
                                        .and(parameterized(ParametrizationTypeEnum.ATTRIBUTION)))),
                        Holder::new)
                        .apply(table(TableEnum.VISITS),
                                (d, h) -> {
                                    h.setDate1(START_DATE);
                                    h.setDate2(END_DATE);
                                    h.getTail().append(
                                            new CommonReportParameters()
                                                    .withId(COUNTER.get(ID))
                                                    .withMetrics(user.onMetadataSteps()
                                                            .getMetrics(favorite().and(table(TableEnum.VISITS)))),
                                            goalId(COUNTER.get(Counter.GOAL_ID)));
                                    return Stream.of(Pair.of(d, h));
                                })
                        .apply(table(TableEnum.ADVERTISING),
                                (d, h) -> {
                                    h.setDate1(ADVERTISING_START_DATE);
                                    h.setDate2(ADVERTISING_END_DATE);
                                    h.getTail().append(
                                            new CommonReportParameters()
                                                    .withId(ADVERTISING_COUNTER)
                                                    .withAccuracy("0.001")
                                                    .withMetrics(user.onMetadataSteps()
                                                            .getMetrics(favorite().and(table(TableEnum.ADVERTISING))))
                                                    .withDirectClientLogins(
                                                            user.onManagementSteps().onClientSteps().getClientLogins(
                                                                    new ClientsParameters()
                                                                            .withCounters(ADVERTISING_COUNTER.get(ID))
                                                                            .withDate1(ADVERTISING_START_DATE)
                                                                            .withDate2(ADVERTISING_END_DATE),
                                                                    ulogin(ADVERTISING_COUNTER.get(U_LOGIN)))),
                                            goalId(ADVERTISING_COUNTER.get(Counter.GOAL_ID)),
                                            currency("643"));
                                    return Stream.of(Pair.of(d, h));
                                })
                        .buildVectorValues(identity()))
                .build();
    }

    @Before
    public void setup() {
        result = user.onReportSteps().getReportAndExpectSuccess(
                requestType,
                dateParameters.apply(holder.getDate1(), holder.getDate2()),
                new CommonReportParameters()
                        .withDimension(dimensionName)
                        .withLimit(1),
                new ParametrizationParameters()
                        .withAttribution(attribution),
                holder.getTail());
    }

    @Test
    public void attributionTest() {
        assertThat("значение параметра attribution совпадает с ожидаемым", result.getAttribution(),
                attributionEqualTo(attribution));
    }
}
