package ru.yandex.autotests.metrika.tests.ft.report.visitors;

import com.google.common.collect.Sets;
import org.junit.Before;
import org.junit.Test;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.beans.schemes.StatV1UserInfoGETSchema;
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
@Title("Информация о посетителе")
public class VisitorInfoTest {

    private static final String USER_ID_HASH_DIMENSION = "ym:u:userIDHash";
    private static final String USER_ID_HASH_64_DIMENSION = "ym:u:userIDHash64";
    private static final String FIRST_VISIT_DATE_DIMENSION = "ym:u:userFirstVisitDate";

    private static final String USER_ID_HASH = "2630006639";
    private static final String USER_ID_HASH_64 = "5472866708289854893";
    private static final String FIRST_VISIT_DATE = "2018-07-03";

    private static final Set<String> dimensions = new HashSet<>(Arrays.asList(
            "ym:u:userIDHash",
            "ym:u:userIDHash64",
            "ym:u:userComment",
            "ym:u:regionAggregated",
            "ym:u:deviceCategory",
            "ym:u:operatingSystem",
            "ym:u:userFirstVisitDate",
            "ym:u:lastVisitTime",
            "ym:u:userActivity",
            "ym:u:userVisits",
            "ym:u:totalVisitsDuration",
            "ym:u:userGoals",
            "ym:u:webVisorUserParamsAll",
            "ym:u:browser",
            "ym:u:purchaseNumber",
            "ym:u:userRevenueFull",
            "ym:u:clientID",
            "ym:u:firstTrafficSource",
            "ym:u:mobilePhone",
            "ym:u:mobilePhoneModel",
            "ym:u:refererDomainShort",
            "ym:u:socialNetwork",
            "ym:u:WVAdvEngine",
            "ym:u:userOfflineCalls"
    ));


    private static Long counterId = Counters.MELDA_RU.getId();
    private static UserSteps owner = new UserSteps().withUser(METRIKA_TEST_COUNTERS);

    private StatV1UserInfoGETSchema info;

    @Before
    public void setup() {
        VisitorInfoParameters params = new VisitorInfoParameters()
                .withId(counterId)
                .withUserIdHash(USER_ID_HASH)
                .withUserIdHash64(USER_ID_HASH_64)
                .withFirstVisitDate(FIRST_VISIT_DATE);
        info = owner.onVisitorsSteps().getVisitorInfoAndExpectSuccess(params);
    }

    @Test
    public void userIdHashTest() {
        int userIdHashIndex = info.getQuery().getDimensions().indexOf(USER_ID_HASH_DIMENSION);
        String value = (String) info.getData().get(0).getDimensions().get(userIdHashIndex).get("name");
        assertThat("userIdHash совпадает с ожидаемым", value, equalTo(USER_ID_HASH));
    }

    @Test
    public void userIdHash64Test() {
        int userIdHash64Index = info.getQuery().getDimensions().indexOf(USER_ID_HASH_64_DIMENSION);
        String value = (String) info.getData().get(0).getDimensions().get(userIdHash64Index).get("name");
        assertThat("userIdHash64 совпадает с ожидаемым", value, equalTo(USER_ID_HASH_64));
    }

    @Test
    public void firstVisitDateTest() {
        int firstVisitDateIndex = info.getQuery().getDimensions().indexOf(FIRST_VISIT_DATE_DIMENSION);
        String value = (String) info.getData().get(0).getDimensions().get(firstVisitDateIndex).get("name");
        assertThat("Дата первого визита совпадает с ожидаемой", value, equalTo(FIRST_VISIT_DATE));
    }

    @Test
    public void dimensionsTest() {
        assertThat("В ответе есть все необходимые измерения", Sets.difference(new HashSet<>(info.getQuery().getDimensions()), dimensions).isEmpty(), equalTo(true));
    }
}
