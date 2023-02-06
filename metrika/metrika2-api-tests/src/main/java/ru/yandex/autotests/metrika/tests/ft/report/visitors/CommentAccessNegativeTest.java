package ru.yandex.autotests.metrika.tests.ft.report.visitors;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.junit.runners.Parameterized.Parameter;
import org.junit.runners.Parameterized.Parameters;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.autotests.metrika.data.common.counters.Counters;
import ru.yandex.autotests.metrika.data.common.users.User;
import ru.yandex.autotests.metrika.data.parameters.visitors.VisitorCommentParameters;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.external.GrantE;
import ru.yandex.metrika.api.management.client.external.GrantType;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static com.google.common.collect.ImmutableList.of;
import static ru.yandex.autotests.metrika.data.common.users.User.LOGIN;
import static ru.yandex.autotests.metrika.data.common.users.Users.*;
import static ru.yandex.autotests.metrika.data.parameters.StaticParameters.ignoreQuota;
import static ru.yandex.autotests.metrika.errors.ManagementError.ACCESS_DENIED;
import static ru.yandex.autotests.metrika.errors.ManagementError.UNAUTHORIZED;

@Features(Requirements.Feature.VISITORS)
@Stories({Requirements.Story.Visitors.COMMENTS})
@Title("Доступ к комментариям (негативные тесты)")
@RunWith(Parameterized.class)
public class CommentAccessNegativeTest {

    private static final String USER_ID_HASH = "3543544117";
    private static final String USER_ID_HASH_64 = "10530073078559821571";
    private static final String FIRST_VISIT_DATE = "2018-02-08";

    private static final User GUEST_VIEW = USER_FOR_EMAIL_SUBSCRIPTION4;
    private static final User OWNER = METRIKA_TEST_COUNTERS;
    private final static User ANONYMOUS = USER_WITH_EMPTY_TOKEN;

    private static Long counterId;
    private static UserSteps owner;

    private UserSteps user;

    @Parameter(0)
    public User userParam;

    @Parameter(1)
    public String title;

    @Parameter(2)
    public IExpectedError error;

    @Parameters(name = "Пользователь: {0}, доступ: {1}")
    public static Collection<Object[]> createParameters() {
        return of(
                new Object[] {ANONYMOUS, "Неавторизованный", UNAUTHORIZED},
                new Object[] {MANAGER, "Менеджер", ACCESS_DENIED},
                new Object[] {YAMANAGER, "Менеджер Яндекса", ACCESS_DENIED},
                new Object[] {MANAGER_DIRECT, "Менеджер Директа", ACCESS_DENIED},
                new Object[] {GUEST_VIEW, "Пользователь с гостевым доступом на чтение", ACCESS_DENIED},
                new Object[] {SIMPLE_USER, "Авторизованный пользователь без доступа к счетчику", ACCESS_DENIED}
        );
    }

    @Before
    public void setup() {
        owner = new UserSteps().withUser(OWNER);
        counterId = Counters.MELDA_RU.getId();
        owner.onManagementSteps().onGrantsSteps().setGrantAndExpectSuccess(
                counterId,
                new GrantE().withPerm(GrantType.VIEW).withUserLogin(GUEST_VIEW.get(LOGIN)),
                ignoreQuota(true)
        );
        user = new UserSteps().withUser(userParam);
    }

    @Test
    public void addCommentTest() {
        user.onVisitorsSteps().addCommentAndExpectError(error, new VisitorCommentParameters()
                .withComment("comment")
                .withId(counterId)
                .withUserIdHash(USER_ID_HASH)
                .withUserIdHash64(USER_ID_HASH_64)
                .withFirstVisitDate(FIRST_VISIT_DATE)
        );
    }

    @Test
    public void deleteCommentTest() {
        user.onVisitorsSteps().deleteCommentAndExpectError(error, new VisitorCommentParameters()
                .withId(counterId)
                .withUserIdHash(USER_ID_HASH)
                .withUserIdHash64(USER_ID_HASH_64)
                .withFirstVisitDate(FIRST_VISIT_DATE)
        );
    }

    @After
    public void cleanUp() {
        owner.onManagementSteps().onGrantsSteps().deleteGrantAndExpectSuccess(counterId, GUEST_VIEW.get(LOGIN));
    }
}
