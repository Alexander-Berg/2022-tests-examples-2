package ru.yandex.autotests.metrika.tests.b2b.inpage.segmentation;

import java.util.List;

import org.junit.runners.Parameterized;

import ru.yandex.autotests.metrika.beans.schemes.StatV1DataGETSchema;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.parameters.FreeFormParameters;
import ru.yandex.autotests.metrika.data.parameters.report.v1.TableReportParameters;
import ru.yandex.autotests.metrika.filters.Term;
import ru.yandex.autotests.metrika.tests.b2b.BaseB2bTest;

import static ru.yandex.autotests.metrika.data.common.counters.Counters.INOPTIKA_RU;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.OPENTECH;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.SENDFLOWERS_RU;
import static ru.yandex.autotests.metrika.data.parameters.FreeFormParameters.makeParameters;
import static ru.yandex.autotests.metrika.data.parameters.report.v1.GoalIdParameters.goalId;
import static ru.yandex.autotests.metrika.filters.Term.dimension;

/**
 * Created by sourx on 27.10.16.
 */
public abstract class B2bInpageSegmentationDimensionBaseTest extends BaseB2bTest {
    private static final String METRIC = "ym:s:visits";

    protected static final String URL = "https://novosibirsk.e2e4online.ru/";
    protected static final Counter COUNTER = OPENTECH;

    protected static final String SCROLL_MAP_URL = "https://inoptika.ru/";
    protected static final Counter SCROLL_MAP_COUNTER = INOPTIKA_RU;

    protected static final Counter PARAMS_LEVEL_AND_SEARCH_PHRASE_COUNTER = SENDFLOWERS_RU;
    protected static final String PARAMS_LEVEL_AND_SEARCH_PHRASE_URL = "https://www.sendflowers.ru/";

    @Parameterized.Parameter()
    public String dimension;

    @Parameterized.Parameter(1)
    public Holder holder;

    static class Holder {
        private FreeFormParameters tail = makeParameters();
        private Counter counter;
        private String url;
        private String date1;
        private String date2;
        private String filter;

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

        public String getFilter() {
            return filter;
        }

        public Holder setFilter(String filter) {
            this.filter = filter;
            return this;
        }
    }

    @Override
    protected void assumeOnResponses(Object testingBean, Object referenceBean) {
        super.assumeOnResponses(testingBean, referenceBean);
        userOnTest.onResultSteps().assumeSuccessBoth(testingBean, referenceBean);
        userOnTest.onResultSteps().assumeInpageReportsNotEmptyBoth(testingBean, referenceBean);
    }

    protected String getFilter() {
        TableReportParameters simpleReportParameters = new TableReportParameters()
                .withId(holder.getCounter())
                .withMetric(METRIC)
                .withDimension(dimension)
                .withDate1(holder.getDate1())
                .withDate2(holder.getDate2())
                .withLimit(1)
                .withAccuracy("1");

        StatV1DataGETSchema result = userOnTest.onReportFacedSteps()
                .getTableReportAndExpectSuccess(simpleReportParameters, goalId(holder.getCounter()));

        List<List<String>> dimensionsList = userOnTest.onResultSteps().getDimensions(result);
        String dimensionValue = dimensionsList.get(0).get(0);
        Term term = dimension(dimension);
        if (dimensionValue == null) {
            term.notDefined();
        } else {
            term.equalTo(dimensionValue);
        }
        return term.build();
    }
}
