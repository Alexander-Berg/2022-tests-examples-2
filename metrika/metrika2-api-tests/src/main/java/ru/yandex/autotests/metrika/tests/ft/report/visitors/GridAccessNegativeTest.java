package ru.yandex.autotests.metrika.tests.ft.report.visitors;

import com.google.common.collect.ImmutableMap;
import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.common.users.User;
import ru.yandex.autotests.metrika.data.parameters.report.v1.TableReportParameters;
import ru.yandex.autotests.metrika.data.parameters.visitors.VisitorInfoParameters;
import ru.yandex.autotests.metrika.errors.ManagementError;
import ru.yandex.autotests.metrika.commons.rules.IgnoreParameters;
import ru.yandex.autotests.metrika.commons.rules.ParametersIgnoreRule;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;
import java.util.Map;

import static com.google.common.collect.ImmutableList.of;
import static java.util.Arrays.asList;
import static org.hamcrest.core.IsEqual.equalTo;
import static ru.yandex.autotests.metrika.data.common.CounterConstants.PUBLIC_COUNTER;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.MELDA_RU;
import static ru.yandex.autotests.metrika.data.common.users.Users.*;

@Features(Requirements.Feature.VISITORS)
@Stories({Requirements.Story.Visitors.COMMENTS})
@Title("Доступ к информации о посетителе (негативные тесты)")
@RunWith(Parameterized.class)
public class GridAccessNegativeTest {

    private static final Map<Long, UserInfo> userInfo = ImmutableMap.of(
            MELDA_RU.getId(), new UserInfo("1228125527", "12885858787377372863", "2018-07-02"),
            PUBLIC_COUNTER.getId(), new UserInfo("849202619", "10200525135763458380", "2018-07-04")
    );

    private final static User UNAUTHORIZED = USER_WITH_EMPTY_TOKEN;

    private Long counterId;
    private UserSteps user;

    @Rule
    public ParametersIgnoreRule ignoreRule = new ParametersIgnoreRule();

    @Parameterized.Parameter(0)
    public Counter counter;

    @Parameterized.Parameter(1)
    public User userParam;

    @Parameterized.Parameter(2)
    public String title;

    @Parameterized.Parameters(name = "Счетчик: {0}, пользователь: {1}, доступ: {2}")
    public static Collection<Object[]> createParameters() {
        return of(
                new Object[] {MELDA_RU, UNAUTHORIZED, "Неавторизованный"},
                new Object[] {MELDA_RU, YAMANAGER, "Менеджер Яндекса"},
                new Object[] {MELDA_RU, SIMPLE_USER, "Авторизованный пользователь без доступа к счетчику"},
                new Object[] {PUBLIC_COUNTER, UNAUTHORIZED, "Неавторизованный"},
                new Object[] {PUBLIC_COUNTER, SIMPLE_USER, "Авторизованный пользователь без доступа к счетчику"}
        );
    }

    @Before
    public void setup() {
        counterId = counter.getId();
        user = new UserSteps().withUser(userParam);
    }

    @Test
    @IgnoreParameters(reason = "METR-29257", tag = "METR-29257")
    public void visitorInfoTest() {
        UserInfo userInfo = GridAccessNegativeTest.userInfo.get(counterId);
        user.onVisitorsSteps().getVisitorInfoAndExpectError(ManagementError.ACCESS_DENIED, new VisitorInfoParameters()
                .withId(counterId)
                .withUserIdHash(userInfo.userIdHash)
                .withUserIdHash64(userInfo.userIdHash64)
                .withFirstVisitDate(userInfo.firstVisitDate)
        );
    }

    @Test
    @IgnoreParameters(reason = "METR-29257", tag = "METR-29257")
    public void visitorVisitsTest() {
        UserInfo userInfo = GridAccessNegativeTest.userInfo.get(counterId);
        user.onVisitorsSteps().getVisitorVisitsAndExpectError(ManagementError.ACCESS_DENIED, new VisitorInfoParameters()
                .withId(counterId)
                .withUserIdHash(userInfo.userIdHash)
                .withUserIdHash64(userInfo.userIdHash64)
                .withFirstVisitDate(userInfo.firstVisitDate)
        );
    }

    @Test
    @IgnoreParameters(reason = "METR-29257", tag = "METR-29257")
    public void visitorsGridTest() {
        user.onVisitorsSteps().getVisitorsGridAndExpectError(
                ManagementError.ACCESS_DENIED,
                new TableReportParameters().withId(counterId));
    }

    @IgnoreParameters.Tag(name = "METR-29257")
    public static Collection<Object[]> ignoreMETR29257() {
        return asList(new Object[][] {
                { equalTo(PUBLIC_COUNTER), equalTo(SIMPLE_USER), equalTo("Авторизованный пользователь без доступа к счетчику") }
        });
    }


    private static class UserInfo {
        private final String userIdHash;
        private final String userIdHash64;
        private final String firstVisitDate;

        UserInfo(String userIdHash, String userIdHash64, String firstVisitDate) {
            this.userIdHash = userIdHash;
            this.userIdHash64 = userIdHash64;
            this.firstVisitDate = firstVisitDate;
        }
    }

}
