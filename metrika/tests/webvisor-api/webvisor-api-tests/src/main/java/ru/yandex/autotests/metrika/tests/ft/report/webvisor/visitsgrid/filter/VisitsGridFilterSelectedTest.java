package ru.yandex.autotests.metrika.tests.ft.report.webvisor.visitsgrid.filter;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.beans.schemes.WebvisorV2DataVisitsGETSchema;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.parameters.webvisor.v2.VisitViewedParameters;
import ru.yandex.autotests.metrika.data.parameters.webvisor.v2.VisitsGridParameters;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.List;

import static org.hamcrest.Matchers.*;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.SENDFLOWERS_RU;
import static ru.yandex.autotests.metrika.data.common.users.Users.SUPPORT;
import static ru.yandex.autotests.metrika.filters.Term.dimension;
import static ru.yandex.autotests.metrika.utils.AllureUtils.addTestParameter;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

/**
 * Created by sourx on 06.04.17.
 */
@Features(Requirements.Feature.WEBVISOR)
@Stories({Requirements.Story.WebVisor.VISITS_GRID})
@Title("Вебвизор: таблица визитов, фильтрация по избранным визитам")
public class VisitsGridFilterSelectedTest {
    private static final Counter counter = SENDFLOWERS_RU;

    private static final String VISIT_ID = "ym:s:visitID";
    private static final String START_DATE = "7daysAgo";
    private static final String END_DATE = "7daysAgo";
    private static final String DIMENSION = "ym:s:webVisorSelected";
    private static UserSteps user;

    private List<String> requiredDimensionNames;

    private String filter;

    private String visitId;

    @Before
    public void setup() {
        user = new UserSteps().withUser(SUPPORT);

        requiredDimensionNames = user.onWebVisorMetadataSteps().getWebVisorDefaultVisitDimensions().getRequired();

        filter = dimension(DIMENSION).equalTo("Yes").build();

        visitId = getVisitId();

        user.onWebVisorSteps().addSelectedVisitsAndExpectSuccess(new VisitViewedParameters()
                .withVisitId(visitId)
                .withId(counter));

        addTestParameter("Фильтр", filter);
    }

    @Test
    public void visitsGridFilterBySelectedTest() {
        VisitsGridParameters reportParameters = getReportParameters().withFilters(filter);

        WebvisorV2DataVisitsGETSchema result = user.onWebVisorSteps().getVisitsGridAndExpectSuccess(reportParameters);

        List<String> selectedVisitIds = user.onResultSteps().getDimensionValues(VISIT_ID, result);

        assertThat("избранные визиты присутствуют", selectedVisitIds, hasItem(visitId));
    }

    private String getVisitId() {
        VisitsGridParameters visitsGridReportParameters = getReportParameters().withLimit(1);

        WebvisorV2DataVisitsGETSchema visitsGrid =
                user.onWebVisorSteps().getVisitsGridAndExpectSuccess(visitsGridReportParameters);

        List<String> visitIds = user.onResultSteps().getDimensionValues(VISIT_ID, visitsGrid);

        assertThat("для теста доступен визит", visitIds, iterableWithSize(greaterThanOrEqualTo(1)));

        return visitIds.get(0);
    }

    private VisitsGridParameters getReportParameters() {
        return new VisitsGridParameters()
                .withId(counter)
                .withDimensions(requiredDimensionNames)
                .withDate1(START_DATE)
                .withDate2(END_DATE);
    }

    @After
    public void teardown() {
        if (visitId != null)
            user.onWebVisorSteps().deleteSelectedVisitAndExpectSuccess(new VisitViewedParameters()
                    .withVisitId(visitId)
                    .withId(counter));
    }
}
