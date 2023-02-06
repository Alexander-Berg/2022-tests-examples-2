package ru.yandex.autotests.metrika.tests.ft.report.visitors;

import com.google.common.collect.Sets;
import org.junit.Before;
import org.junit.Test;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.beans.schemes.StatV1UserListGETSchema;
import ru.yandex.autotests.metrika.data.common.counters.Counters;
import ru.yandex.autotests.metrika.data.parameters.report.v1.CommonReportParameters;
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
@Title("Грид посетителей")
public class GridTest {

    private static final Set<String> dimensions = new HashSet<>(Arrays.asList(
            "ym:u:userIDHash",
            "ym:u:userIDHash64",
            "ym:u:userComment",
            "ym:u:regionCountry",
            "ym:u:deviceCategory",
            "ym:u:operatingSystem",
            "ym:u:operatingSystemRoot",
            "ym:u:userFirstVisitDate",
            "ym:u:lastVisitTime",
            "ym:u:userActivity",
            "ym:u:userVisits",
            "ym:u:totalVisitsDuration",
            "ym:u:userGoals",
            "ym:u:userOfflineCalls",
            "ym:u:purchaseNumber",
            "ym:u:userRUBRevenue"
    ));


    private static Long counterId = Counters.MELDA_RU.getId();
    private static UserSteps owner = new UserSteps().withUser(METRIKA_TEST_COUNTERS);

    private StatV1UserListGETSchema grid;

    @Before
    public void setup() {
        grid = owner.onVisitorsSteps().getVisitorsGridAndExpectSuccess(new CommonReportParameters().withId(counterId));
    }

    @Test
    public void dimensionsTest() {
        assertThat("В ответе есть все необходимые измерения", Sets.difference(new HashSet<>(grid.getQuery().getDimensions()), dimensions).isEmpty(), equalTo(true));
    }
}
