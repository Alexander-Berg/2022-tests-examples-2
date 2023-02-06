package ru.yandex.autotests.metrika.tests.ft.report.webvisor.visitsgrid.filter;

import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.beans.schemes.WebvisorV2DataVisitsGETSchema;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.metadata.v1.ParameterValues;
import ru.yandex.autotests.metrika.data.parameters.webvisor.v2.VisitsGridParameters;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.List;

import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.on;
import static org.hamcrest.Matchers.greaterThan;
import static org.hamcrest.Matchers.iterableWithSize;
import static ru.yandex.autotests.metrika.data.common.counters.Counter.ID;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.SENDFLOWERS_RU;
import static ru.yandex.autotests.metrika.data.metadata.v1.enums.ParametrizationTypeEnum.GOAL_ID;
import static ru.yandex.autotests.metrika.filters.Term.dimension;
import static ru.yandex.autotests.metrika.utils.AllureUtils.addTestParameter;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

/**
 * Created by konkov on 22.12.2014.
 */
@Features(Requirements.Feature.WEBVISOR)
@Stories({Requirements.Story.WebVisor.VISITS_GRID})
@Title("Вебвизор: таблица визитов, фильтрация по целям")
public class VisitsGridFilterByGoalTest {

    private static final Counter counter = SENDFLOWERS_RU;

    private static final String START_DATE = "14daysAgo";
    private static final String END_DATE = "7daysAgo";
    private static final String DIMENSION = "ym:s:goal<goal_id>IsReached";
    private static UserSteps user;

    private List<String> requiredDimensionNames;

    private String filter;

    @BeforeClass
    public static void init() {
        user = new UserSteps();
    }

    @Before
    public void setup() {
        requiredDimensionNames = user.onWebVisorMetadataSteps().getWebVisorDefaultVisitDimensions().getRequired();

        filter = getFilter();

        addTestParameter("Фильтр", filter);
    }

    @Test
    public void visitsGridFilterByGoalTest() {
        VisitsGridParameters reportParameters = getReportParameters();
        reportParameters.setFilters(filter);

        WebvisorV2DataVisitsGETSchema result = user.onWebVisorSteps().getVisitsGridAndExpectSuccess(reportParameters);

        assertThat("визиты для заданной цели присутствуют", result,
                having(on(WebvisorV2DataVisitsGETSchema.class).getData(), iterableWithSize(greaterThan(0))));
    }

    private VisitsGridParameters getReportParameters() {
        VisitsGridParameters reportParameters = new VisitsGridParameters();
        reportParameters.setId(counter.get(ID));
        reportParameters.setDimensions(requiredDimensionNames);
        reportParameters.setDate1(START_DATE);
        reportParameters.setDate2(END_DATE);

        return reportParameters;
    }

    private String getFilter() {
        return dimension(getDimension()).equalTo("Yes").build();
    }

    private String getDimension() {
        return getParameterValue().substitute(DIMENSION);
    }

    private ParameterValues getParameterValue() {
        return new ParameterValues().append(GOAL_ID, String.valueOf(counter.get(Counter.GOAL_ID)));
    }

}
