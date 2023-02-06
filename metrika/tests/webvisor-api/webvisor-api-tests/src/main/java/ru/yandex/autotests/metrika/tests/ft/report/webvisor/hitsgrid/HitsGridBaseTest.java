package ru.yandex.autotests.metrika.tests.ft.report.webvisor.hitsgrid;

import org.junit.Before;
import org.junit.Test;
import ru.yandex.autotests.irt.testutils.json.JsonUtils;
import ru.yandex.autotests.metrika.beans.schemes.WebvisorV2DataHitsGETSchema;
import ru.yandex.autotests.metrika.beans.schemes.WebvisorV2DataVisitsGETSchema;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.parameters.webvisor.v2.HitsGridParameters;
import ru.yandex.autotests.metrika.data.parameters.webvisor.v2.VisitsGridParameters;
import ru.yandex.autotests.metrika.steps.UserSteps;

import java.util.List;

import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.on;
import static com.google.common.collect.ImmutableList.of;
import static java.lang.String.format;
import static org.hamcrest.Matchers.*;
import static org.junit.runners.Parameterized.Parameter;
import static ru.yandex.autotests.metrika.data.common.counters.Counter.ID;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.AT_NEW_WEBVISOR;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.SENDFLOWERS_RU;
import static ru.yandex.autotests.metrika.matchers.Matchers.iterableHasDimensionValuesFilled;
import static ru.yandex.autotests.metrika.utils.AllureUtils.*;

/**
 * Created by konkov on 10.12.2014.
 */
public abstract class HitsGridBaseTest {
    protected static final List<Counter> COUNTERS = of(SENDFLOWERS_RU, AT_NEW_WEBVISOR);

    private static final String VISIT_ID = "ym:s:visitID";
    private static final String WATCH_ID = "ym:pv:watchID";
    private static final String DAY_NUMBER = "ym:pv:dayNumber";

    protected final static UserSteps user = new UserSteps();

    private static String visitId;

    @Parameter()
    public List<String> dimensions;

    @Parameter(1)
    public static Counter counter;

    protected WebvisorV2DataHitsGETSchema report;

    private String getVisitId() {
        VisitsGridParameters visitsGridReportParameters = new VisitsGridParameters();
        visitsGridReportParameters.setLimit(1);
        visitsGridReportParameters.setId(counter.get(ID));
        visitsGridReportParameters.setDimensions(getRequiredVisitsGridDimensions());

        WebvisorV2DataVisitsGETSchema visitsGrid =
                user.onWebVisorSteps().getVisitsGridAndExpectSuccess(visitsGridReportParameters);

        List<String> visitIds = user.onResultSteps().getDimensionValues(VISIT_ID, visitsGrid);

        assertThat("для теста доступен визит", visitIds, iterableWithSize(greaterThanOrEqualTo(1)));

        return visitIds.get(0);
    }

    private static List<String> getRequiredVisitsGridDimensions() {
        return user.onWebVisorMetadataSteps().getWebVisorDefaultVisitDimensions().getRequired();
    }

    @Before
    public void setup() {
        visitId = getVisitId();
        HitsGridParameters reportParameters = new HitsGridParameters();
        reportParameters.setId(counter.get(ID));
        reportParameters.setVisitId(visitId);
        reportParameters.setDimensions(dimensions);

        addJsonAttachment("Атрибуты", JsonUtils.toString(dimensions));

        report = user.onWebVisorSteps().getHitsGridAndExpectSuccess(reportParameters);

        assumeThat("данные для теста присутствуют", report,
                having(on(WebvisorV2DataHitsGETSchema.class).getData(), iterableWithSize(greaterThan(0))));
    }

    @Test
    public void hitsGridWatchIdTest() {
        List<String> dimensionValues = user.onResultSteps().getDimensionValues(WATCH_ID, report);

        assertThat(format("поле %s заполнено", WATCH_ID), dimensionValues,
                iterableHasDimensionValuesFilled());
    }

    @Test
    public void hitsGridDayNumberTest() {
        List<String> dimensionValues = user.onResultSteps().getDimensionValues(DAY_NUMBER, report);

        assertThat(format("поле %s заполнено", WATCH_ID), dimensionValues,
                iterableHasDimensionValuesFilled());
    }
}
