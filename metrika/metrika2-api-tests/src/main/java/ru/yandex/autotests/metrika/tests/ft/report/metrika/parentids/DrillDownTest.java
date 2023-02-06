package ru.yandex.autotests.metrika.tests.ft.report.metrika.parentids;

import com.google.common.collect.ImmutableList;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.beans.schemes.StatV1DataDrilldownGETSchema;
import ru.yandex.autotests.metrika.data.common.DateConstants;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.parameters.management.v1.ClientsParameters;
import ru.yandex.autotests.metrika.data.parameters.report.v1.DrillDownReportParameters;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.constructor.response.DrillDownRow;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;
import java.util.List;

import static com.google.common.collect.ImmutableList.of;
import static java.lang.String.format;
import static org.apache.commons.lang3.ArrayUtils.toArray;
import static org.hamcrest.Matchers.equalTo;
import static org.junit.runners.Parameterized.Parameter;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.*;
import static ru.yandex.autotests.metrika.data.parameters.FreeFormParameters.makeParameters;
import static ru.yandex.autotests.metrika.data.parameters.management.v1.DelegateParameters.ulogin;
import static ru.yandex.autotests.metrika.filters.Term.dimension;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

/**
 * Created by konkov on 21.10.2014.
 */
@Features(Requirements.Feature.REPORT)
@Stories({Requirements.Story.Report.Parameter.PARENT_ID, Requirements.Story.Report.Type.DRILLDOWN})
@Title("Отчет Drilldown, parent_ids и expand")
@RunWith(Parameterized.class)
public class DrillDownTest {

    private static final UserSteps user = new UserSteps().withDefaultAccuracy();
    private static final Counter COUNTER = YANDEX_METRIKA;
    private static final String START_DATE = "2016-02-01";
    private static final String END_DATE = "2016-02-29";

    private static final Collection<String> VISIT_METRIC_NAMES = of("ym:s:users");

    private static final Collection<String> VISIT_DIMENSION_NAMES = of(
            "ym:s:startURLPathLevel1",
            "ym:s:startURLPathLevel2",
            "ym:s:startURLPathLevel3",
            "ym:s:startURLPathLevel4",
            "ym:s:startURLPathLevel5",
            "ym:s:endURLPathLevel1",
            "ym:s:endURLPathLevel2",
            "ym:s:endURLPathLevel3",
            "ym:s:endURLPathLevel4",
            "ym:s:endURLPathLevel5");

    private static final Collection<String> HIT_METRIC_NAMES = of("ym:pv:users");

    private static final Collection<String> HIT_DIMENSION_NAMES = of(
            "ym:pv:URLPathLevel1",
            "ym:pv:URLPathLevel2",
            "ym:pv:URLPathLevel3",
            "ym:pv:URLPathLevel4",
            "ym:pv:URLPathLevel5",
            "ym:pv:refererPathLevel1",
            "ym:pv:refererPathLevel2",
            "ym:pv:refererPathLevel3",
            "ym:pv:refererPathLevel4",
            "ym:pv:refererPathLevel5");

    private static final Collection<String> BROWSER_METRIC_NAMES = of(
            "ym:s:users",
            "ym:s:manPercentage");

    private static final Collection<String> BROWSER_DIMENSION_NAMES = of(
            "ym:s:browser",
            "ym:s:browserAndVersionMajor",
            "ym:s:browserAndVersion");

    private static final Collection<String> VISIT_PARAMS_DIMENSION_NAMES = of(
            "ym:s:paramsLevel1",
            "ym:s:paramsLevel2",
            "ym:s:paramsLevel3",
            "ym:s:paramsLevel4",
            "ym:s:paramsLevel5");

    private static final Counter AD_COUNTER = SHATURA_COM;
    private static final String AD_START_DATE = "2016-02-01";
    private static final String AD_END_DATE = "2016-02-29";

    private static final Collection<String> AD_METRIC_NAMES = of(
            "ym:ad:clicks",
            "ym:ad:visits");

    private static final Collection<String> AD_DIMENSION_NAMES = of(
            "ym:ad:directOrder",
            "ym:ad:directPhraseOrCond",
            "ym:ad:directBannerGroup");

    private static final Counter ECOMMERCE_COUNTER = ECOMMERCE_TEST;
    private static final String ECOMMERCE_START_DATE = DateConstants.Ecommerce.START_DATE;
    private static final String ECOMMERCE_END_DATE = DateConstants.Ecommerce.END_DATE;

    private static final Collection<String> ECOMMERCE_METRIC_NAMES = user.onMetadataSteps().getMetricsEcommerceOrders();

    private static final Collection<String> ECOMMERCE_DIMENSION_NAMES = of(
            "ym:s:PPurchaseID",
            "ym:s:PProduct",
            "ym:s:PProductName");

    @Parameter()
    public Collection<String> dimensionNames;

    @Parameter(1)
    public Collection<String> metrics;

    @Parameter(2)
    public List<String> parentIds;

    @Parameter(3)
    public Boolean expand;

    @Parameter(4)
    public String expandDimensionValue;

    @Parameter(5)
    public IFormParameters additionalParameters;

    private DrillDownRow resultRow;

    @Parameterized.Parameters(name = "parent_id={2}")
    public static Collection<Object[]> createParameters() {
        return ImmutableList.<Object[]>builder()
                .add(param(HIT_DIMENSION_NAMES, HIT_METRIC_NAMES,
                        of(),
                        true,
                        "http://old.metrika.yandex.ru/"))
                .add(param(HIT_DIMENSION_NAMES, HIT_METRIC_NAMES,
                        of("http://metrika.yandex.ru/"),
                        true,
                        "http://metrika.yandex.ru/stat/"))
                .add(param(HIT_DIMENSION_NAMES, HIT_METRIC_NAMES,
                        of("http://metrika.yandex.ru/", "http://metrika.yandex.ru/stat/"),
                        true,
                        "http://metrika.yandex.ru/stat/dashboard/"))
                .add(param(HIT_DIMENSION_NAMES, HIT_METRIC_NAMES,
                        of("http://metrika.yandex.ru/", "http://metrika.yandex.ru/stat/",
                                "http://metrika.yandex.ru/stat/dashboard/"),
                        false,
                        "http://metrika.yandex.ru/stat/dashboard/?counter_id=30574277"))
                .add(param(VISIT_DIMENSION_NAMES, VISIT_METRIC_NAMES,
                        of(),
                        true,
                        "http://old.metrika.yandex.ru/"))
                .add(param(VISIT_DIMENSION_NAMES, VISIT_METRIC_NAMES,
                        of("http://metrika.yandex.ru/"),
                        true,
                        "http://metrika.yandex.ru/stat/"))
                .add(param(HIT_DIMENSION_NAMES, HIT_METRIC_NAMES,
                        of("http://metrika.yandex.ru/", "http://metrika.yandex.ru/stat/"),
                        true,
                        "http://metrika.yandex.ru/stat/dashboard/"))
                .add(param(HIT_DIMENSION_NAMES, HIT_METRIC_NAMES,
                        of("http://metrika.yandex.ru/", "http://metrika.yandex.ru/stat/",
                                "http://metrika.yandex.ru/stat/dashboard/"),
                        false,
                        "http://metrika.yandex.ru/stat/dashboard/?counter_id=30574277"))
                .add(param(BROWSER_DIMENSION_NAMES, BROWSER_METRIC_NAMES,
                        of("3", "3.38"), // Firefox
                        false,
                        "Firefox 38.0"))
                .add(param(VISIT_PARAMS_DIMENSION_NAMES, VISIT_METRIC_NAMES,
                        of(),
                        true,
                        "widgets"))
                .add(param(VISIT_PARAMS_DIMENSION_NAMES, VISIT_METRIC_NAMES,
                        of("widgets"),
                        true,
                        "move"))
                .add(param(VISIT_PARAMS_DIMENSION_NAMES, VISIT_METRIC_NAMES,
                        of("widgets", "move"),
                        true,
                        "s"))
                .add(param(VISIT_PARAMS_DIMENSION_NAMES, VISIT_METRIC_NAMES,
                        of("widgets", "move", "s"),
                        false,
                        "1"))
                .add(param(VISIT_PARAMS_DIMENSION_NAMES, VISIT_METRIC_NAMES,
                        of("widgets"),
                        true,
                        "move",
                        getCounterParameters(),
                        new DrillDownReportParameters()
                                .withFilters(dimension("ym:s:gender").equalTo("male").build())))
                .add(param(AD_DIMENSION_NAMES, AD_METRIC_NAMES,
                        of("5701696"),
                        true,
                        "мебель шатура официальный сайт каталог цены",
                        getAdCounterParameters()))
                .add(param(ECOMMERCE_DIMENSION_NAMES, ECOMMERCE_METRIC_NAMES,
                        of("L1003"),
                        true,
                        "The old box 2",
                        getEcommerceParameters()))
                .add(param(ECOMMERCE_DIMENSION_NAMES, ECOMMERCE_METRIC_NAMES,
                        of("L1003", "The old box 2"),
                        false,
                        "The old box 2",
                        getEcommerceParameters()))
                .build();
    }

    @Before
    public void setup() {
        StatV1DataDrilldownGETSchema result = user.onReportSteps()
                .getDrilldownReportAndExpectSuccess(
                        new DrillDownReportParameters()
                                .withDimensions(dimensionNames)
                                .withMetrics(metrics)
                                .withLimit(10)
                                .withAccuracy("1")
                                .withParentIds(parentIds),
                        additionalParameters);

        resultRow = user.onResultSteps().findRow(result, expandDimensionValue);
    }

    @Test
    public void checkExpand() {
        assertThat(format("дочерние записи %sприсутствуют", expand ? "" : "не "),
                resultRow.getExpand(),
                equalTo(expand));
    }

    private static Object[] param(Collection<String> dimensionNames, Collection<String> metrics, List<String> parentIds,
                                  Boolean expectedExpand, String expandDimensionValue) {
        return param(dimensionNames, metrics, parentIds, expectedExpand, expandDimensionValue,
                getCounterParameters());
    }

    private static IFormParameters getCounterParameters() {
        return new DrillDownReportParameters()
                .withId(COUNTER)
                .withDate1(START_DATE)
                .withDate2(END_DATE);
    }

    private static IFormParameters getAdCounterParameters() {
        return new DrillDownReportParameters()
                .withId(AD_COUNTER)
                .withDate1(AD_START_DATE)
                .withDate2(AD_END_DATE)
                .withDirectClientLogins(user.onManagementSteps().onClientSteps().getClientLogins(
                        new ClientsParameters()
                                .withCounters(AD_COUNTER)
                                .withDate1(AD_START_DATE)
                                .withDate2(AD_END_DATE),
                        ulogin(AD_COUNTER)));
    }

    private static IFormParameters getEcommerceParameters() {
        return new DrillDownReportParameters()
                .withId(ECOMMERCE_COUNTER)
                .withDate1(ECOMMERCE_START_DATE)
                .withDate2(ECOMMERCE_END_DATE);
    }

    private static Object[] param(Collection<String> dimensionNames, Collection<String> metrics, List<String> parentIds,
                                  Boolean expectedExpand, String expandDimensionValue,
                                  IFormParameters... additionalParameters) {
        return toArray(dimensionNames, metrics, parentIds, expectedExpand, expandDimensionValue,
                makeParameters().append(additionalParameters));
    }
}
