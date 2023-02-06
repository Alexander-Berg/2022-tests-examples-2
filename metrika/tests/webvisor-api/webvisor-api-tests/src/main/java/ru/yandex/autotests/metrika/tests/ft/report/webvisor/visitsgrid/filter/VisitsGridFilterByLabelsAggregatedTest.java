//package ru.yandex.autotests.metrika.tests.ft.report.webvisor.visitsgrid.filter;
//
//import org.junit.Before;
//import org.junit.BeforeClass;
//import org.junit.Test;
//import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
//import ru.yandex.autotests.metrika.Requirements;
//import ru.yandex.autotests.metrika.beans.schemes.StatV1DataGETSchema;
//import ru.yandex.autotests.metrika.beans.schemes.WebvisorV2DataVisitsGETSchema;
//import ru.yandex.autotests.metrika.data.common.counters.Counter;
//import ru.yandex.autotests.metrika.data.parameters.report.v1.TableReportParameters;
//import ru.yandex.autotests.metrika.data.parameters.webvisor.v2.VisitsGridParameters;
//import ru.yandex.autotests.metrika.steps.UserSteps;
//import ru.yandex.qatools.allure.annotations.Features;
//import ru.yandex.qatools.allure.annotations.Stories;
//import ru.yandex.qatools.allure.annotations.Title;
//
//import java.util.List;
//
//import static ch.lambdaj.Lambda.having;
//import static ch.lambdaj.Lambda.on;
//import static java.lang.String.format;
//import static org.hamcrest.Matchers.*;
//import static org.hamcrest.core.IsNot.not;
//import static ru.yandex.autotests.metrika.data.common.counters.Counter.ID;
//import static ru.yandex.autotests.metrika.data.common.counters.Counters.SENDFLOWERS_RU;
//import static ru.yandex.autotests.metrika.filters.Term.dimension;
//import static ru.yandex.autotests.metrika.sort.SortBuilder.sort;
//import static ru.yandex.autotests.metrika.utils.AllureUtils.*;
//
///**
// * Created by konkov on 24.12.2014.
// */
//@Features(Requirements.Feature.WEBVISOR)
//@Stories({Requirements.Story.WebVisor.VISITS_GRID})
//@Title("Вебвизор: таблица визитов, фильтрация по меткам")
//public class VisitsGridFilterByLabelsAggregatedTest {
//
//    private static final Counter counter = SENDFLOWERS_RU;
//
//    private static final String START_DATE = "14daysAgo";
//    private static final String END_DATE = "7daysAgo";
//    private static final String DIMENSION = "ym:s:labelsAggregated";
//    private static final String LABEL = "ym:s:UTMSource";
//    private static final String METRIC_VISITS = "ym:s:visits";
//
//    private static UserSteps user;
//
//    private List<String> requiredDimensionNames;
//
//    private String filter;
//
//    @BeforeClass
//    public static void init() {
//        user = new UserSteps();
//    }
//
//    @Before
//    public void setup() {
//        requiredDimensionNames = user.onWebVisorMetadataSteps().getWebVisorDefaultVisitDimensions().getRequired();
//
//        filter = getFilter();
//
//        addTestParameter("Фильтр", filter);
//    }
//
//    @Test
//    public void visitsGridFilterByLabelsAggregatedTest() {
//        VisitsGridParameters reportParameters = getReportParameters();
//        reportParameters.setFilters(filter);
//
//        WebvisorV2DataVisitsGETSchema result = user.onWebVisorSteps().getVisitsGridAndExpectSuccess(reportParameters);
//
//        assertThat("визиты c указанной меткой присутствуют", result,
//                having(on(WebvisorV2DataVisitsGETSchema.class).getData(), iterableWithSize(greaterThan(0))));
//    }
//
//    private VisitsGridParameters getReportParameters() {
//        VisitsGridParameters reportParameters = new VisitsGridParameters();
//        reportParameters.setId(counter.get(ID));
//        reportParameters.setDimensions(requiredDimensionNames, DIMENSION);
//        reportParameters.setDate1(START_DATE);
//        reportParameters.setDate2(END_DATE);
//
//        return reportParameters;
//    }
//
//    private String getFilter() {
//
//        StatV1DataGETSchema result = user.onReportSteps().getTableReportAndExpectSuccess(getTableReportParameters());
//        List<String> dimensionValues = user.onResultSteps().getDimensionValues(LABEL, result);
//
//        assumeThat(format("существуют визиты с не пустым измерением %s", LABEL), dimensionValues,
//                not(empty()));
//
//        return dimension(LABEL).equalTo(dimensionValues.get(0)).build();
//    }
//
//    private IFormParameters getTableReportParameters() {
//        TableReportParameters reportParameters = new TableReportParameters();
//        reportParameters.setId(counter.get(ID));
//        reportParameters.setDimension(LABEL);
//        reportParameters.setMetric(METRIC_VISITS);
//        reportParameters.setSort(sort().by(METRIC_VISITS).descending().build());
//        reportParameters.setLimit(1);
//        reportParameters.setIncludeUndefined(false);
//        reportParameters.setDate1(START_DATE);
//        reportParameters.setDate2(END_DATE);
//        return reportParameters;
//    }
//}
