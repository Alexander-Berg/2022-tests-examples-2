package ru.yandex.autotests.metrika.tests.ft.report.visitors;

import com.google.common.collect.Sets;
import org.junit.Before;
import org.junit.Test;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.beans.schemes.StatV1UserVisitsGETSchema;
import ru.yandex.autotests.metrika.data.common.counters.Counters;
import ru.yandex.autotests.metrika.data.parameters.visitors.VisitorInfoParameters;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Arrays;
import java.util.HashSet;
import java.util.Set;

import static org.hamcrest.core.IsEqual.equalTo;
import static ru.yandex.autotests.metrika.data.common.users.Users.METRIKA_TEST_COUNTERS;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

@Features(Requirements.Feature.VISITORS)
@Stories({Requirements.Story.Visitors.COMMENTS})
@Title("Визиты посетителя")
public class VisitsTest {

    private static final String USER_ID_HASH = "2630006639";
    private static final String USER_ID_HASH_64 = "5472866708289854893";
    private static final String FIRST_VISIT_DATE = "2018-07-03";

    private static final Set<String> dimensions = new HashSet<>(Arrays.asList(
            "ym:s:dateTime",
            "ym:s:visitDuration",
            "ym:s:pageViews",
            "ym:s:trafficSource",
            "ym:s:searchEngine",
            "ym:s:operatingSystem",
            "ym:s:browser",
            "ym:s:deviceCategory",
            "ym:s:bounce",
            "ym:s:screenResolution",
            "ym:s:network",
            "ym:s:visitSerialNumber",
            "ym:s:regionAggregated",
            "ym:s:UTMTerm",
            "ym:s:UTMCampaign",
            "ym:s:UTMContent",
            "ym:s:UTMMedium",
            "ym:s:UTMSource",
            "ym:s:gridEvents",
            "ym:s:visitID",
            "ym:s:webVisorVersion",
            "ym:s:webVisorActivity",
            "ym:s:webVisorGoals",
            "ym:s:hasOfflineCalls",
            "ym:s:refererDomainShort",
            "ym:s:socialNetwork",
            "ym:s:WVAdvEngine",
            "ym:s:parsedParamsRaw"
    ));


    private static Long counterId = Counters.MELDA_RU.getId();
    private static UserSteps owner = new UserSteps().withUser(METRIKA_TEST_COUNTERS);

    private StatV1UserVisitsGETSchema visits;

    @Before
    public void setup() {
        VisitorInfoParameters params = new VisitorInfoParameters()
                .withId(counterId)
                .withUserIdHash(USER_ID_HASH)
                .withUserIdHash64(USER_ID_HASH_64)
                .withFirstVisitDate(FIRST_VISIT_DATE);
        visits = owner.onVisitorsSteps().getVisitorVisitsAndExpectSuccess(params);
    }

    @Test
    public void dimensionsTest() {
        assertThat("В ответе есть все необходимые измерения", Sets.difference(new HashSet<>(visits.getQuery().getDimensions()), dimensions).isEmpty(), equalTo(true));
    }
}
