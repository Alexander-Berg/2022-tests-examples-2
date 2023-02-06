package ru.yandex.autotests.metrika.tests.b2b.inpage.segmentation;

import java.util.Collection;
import java.util.stream.Collectors;
import java.util.stream.Stream;

import org.apache.commons.lang3.tuple.Pair;
import org.junit.Before;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;

import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.beans.schemes.StatV1DataGETSchema;
import ru.yandex.autotests.metrika.commons.junitparams.MultiplicationBuilder;
import ru.yandex.autotests.metrika.commons.rules.IgnoreParameters;
import ru.yandex.autotests.metrika.data.common.DateConstants;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.common.handles.RequestTypes;
import ru.yandex.autotests.metrika.data.metadata.v1.enums.TableEnum;
import ru.yandex.autotests.metrika.data.parameters.FreeFormParameters;
import ru.yandex.autotests.metrika.data.parameters.inpage.v1.InpageDataParameters;
import ru.yandex.autotests.metrika.data.parameters.report.v1.TableReportParameters;
import ru.yandex.autotests.metrika.filters.Term;
import ru.yandex.autotests.metrika.tests.b2b.BaseB2bTest;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static java.util.Arrays.asList;
import static java.util.function.Function.identity;
import static org.hamcrest.Matchers.anything;
import static org.hamcrest.Matchers.either;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.greaterThan;
import static org.hamcrest.Matchers.iterableWithSize;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assumeThat;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.B2B_SUM_PARAMS;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.EUROPA_PLUS;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.INOPTIKA_RU;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.VASHUROK_RU;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.YANDEX_EATS_ON_MAPS;
import static ru.yandex.autotests.metrika.data.metadata.v1.enums.ParametrizationTypeEnum.GOAL_ID;
import static ru.yandex.autotests.metrika.data.parameters.FreeFormParameters.makeParameters;
import static ru.yandex.autotests.metrika.data.parameters.report.v1.GoalIdParameters.goalId;
import static ru.yandex.autotests.metrika.filters.Term.metric;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.any;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.matches;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.offlineCalls;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.parameterized;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.publishers;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.table;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.vacuum;


/**
 * Created by okunev on 20.01.2015.
 */

@Features({Requirements.Feature.DATA, "METRIQA-2115"})
@Stories({Requirements.Story.Inpage.SEGMENTATION})
@Title("B2b - In-page аналитика: проверка сегментации по метрике")
@RunWith(Parameterized.class)
public class B2bInpageSegmentationMetricTest extends BaseB2bTest {
    private static final String START_DATE = "7daysAgo";
    private static final String END_DATE = "yesterday";
    private static final String DIMENSION = "ym:s:browser";
    private static final String URL = "https://www.inoptika.ru/";
    private static final Counter COUNTER = INOPTIKA_RU;
    private static final Counter SUM_PARAMS_COUNTER = B2B_SUM_PARAMS;
    private static final String SUM_PARAMS_URL = "https://www.electrotest.ru/";
    private static final Counter COUNTER_FOR_YAN_METRICS = VASHUROK_RU;
    private static final String URL_FOR_YAN_METRICS = "http://vashurok.ru";

    @Parameterized.Parameter()
    public String metric;

    @Parameterized.Parameter(1)
    public Holder holder;

    static class Holder {
        private FreeFormParameters tail = makeParameters();
        private Counter counter;
        private String url;
        private String date1;
        private String date2;

        public FreeFormParameters getTail() {
            return tail;
        }

        public String getDate1() {
            return date1;
        }

        public Holder setDate1(String date1) {
            this.date1 = date1;
            return this;
        }

        public String getDate2() {
            return date2;
        }

        public Holder setDate2(String date2) {
            this.date2 = date2;
            return this;
        }

        public Counter getCounter() {
            return counter;
        }

        public Holder setCounter(Counter counter) {
            this.counter = counter;
            return this;
        }

        public String getUrl() {
            return url;
        }

        public Holder setUrl(String url) {
            this.url = url;
            return this;
        }
    }

    @Parameterized.Parameters(name = "metric: {0}")
    public static Collection createParameters() {
        return MultiplicationBuilder.<String, String, Holder>builder(
                userOnTest.onMetadataSteps().getMetrics((table(TableEnum.VISITS)).and(offlineCalls().negate())).stream()
                        .filter(x -> !x.matches("ym:s:affinityIndexInterests") && !x.matches("ym:s:affinityIndexInterests2")
                        ).collect(Collectors.toList()),
                Holder::new)
                .apply(any(),
                        (m, h) -> {
                            h.setCounter(COUNTER);
                            h.setDate1(START_DATE);
                            h.setDate2(END_DATE);
                            h.setUrl(URL);

                            return Stream.of(Pair.of(m, h));
                        })
                .apply(parameterized(GOAL_ID), (m, h) -> {
                    h.getTail().append(goalId(h.getCounter()));
                    return Stream.of(Pair.of(m, h));
                })
                .apply(matches(either(equalTo("ym:s:sumParams")).or(equalTo("ym:s:paramsNumber"))),
                        (m, h) -> {
                            h.setCounter(SUM_PARAMS_COUNTER);
                            h.setUrl(SUM_PARAMS_URL);

                            return Stream.of(Pair.of(m, h));
                        })
                .apply(matches(either(equalTo("ym:s:yanRenders")).or(equalTo("ym:s:yanRequests")).or(equalTo("ym:s:yanShows"))),
                        (d, h) -> {
                            h.setCounter(COUNTER_FOR_YAN_METRICS);
                            h.setUrl(URL_FOR_YAN_METRICS);

                            return Stream.of(Pair.of(d, h));
                        })
                .apply(publishers(), (d, h) -> {
                    h.counter = EUROPA_PLUS;
                    h.date1 = DateConstants.Publishers.START_DATE;
                    h.date2 = DateConstants.Publishers.END_DATE;
                    return Stream.of(Pair.of(d, h));
                })
                .apply(vacuum(), (d, h) -> {
                    h.counter = YANDEX_EATS_ON_MAPS;
                    h.date1 = DateConstants.Vacuum.START_DATE;
                    h.date2 = DateConstants.Vacuum.END_DATE;
                    return Stream.of(Pair.of(d, h));
                })
                .build(identity());
    }

    @Before
    public void before() {
        requestType = RequestTypes.INPAGE_CLICK;

        reportParameters = holder.getTail().append(
                new InpageDataParameters()
                        .withAccuracy("1")
                        .withFilter(getFilter())
                        .withId(holder.getCounter())
                        .withDate1(holder.getDate1())
                        .withDate2(holder.getDate2())
                        .withUrl(holder.getUrl()));
    }

    @Override
    protected void assumeOnResponses(Object testingBean, Object referenceBean) {
        super.assumeOnResponses(testingBean, referenceBean);
        userOnTest.onResultSteps().assumeSuccessBoth(testingBean, referenceBean);
        userOnTest.onResultSteps().assumeInpageReportsNotEmptyBoth(testingBean, referenceBean);
    }

    protected String getFilter() {
        TableReportParameters simpleReportParameters = new TableReportParameters()
                .withId(holder.counter)
                .withMetric(metric)
                .withDimension(DIMENSION)
                .withDate1(holder.date1)
                .withDate2(holder.date2)
                .withAccuracy("1");

        StatV1DataGETSchema result = userOnTest.onReportFacedSteps()
                .getTableReportAndExpectSuccess(simpleReportParameters, goalId(holder.counter));

        assumeThat("ответ по запросу с фильтром не пустой", result.getData(),
                iterableWithSize(greaterThan(0)));

        Double metricValue = result.getData().get(0).getMetrics().get(0);
        Term term = metric(metric);
        if (metricValue == null) {
            term.notDefined();
        } else {
            term.equalTo(metricValue);
        }
        return term.build();
    }

    @IgnoreParameters.Tag(name = "pvl")
    public static Collection<Object[]> ignoreParameters() {
        return asList(new Object[][]{
                {equalTo("ym:s:pvl<offline_region>Region<offline_window>Window"), anything()},
                {equalTo("ym:s:pvl<offline_point>Point<offline_window>Window"), anything()}
        });
    }
}
