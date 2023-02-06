package ru.yandex.autotests.metrika.tests.ft.report.visitors;

import org.junit.After;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.junit.runners.Parameterized.Parameter;
import org.junit.runners.Parameterized.Parameters;
import ru.yandex.autotests.irt.testutils.RandomUtils;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.counters.Counters;
import ru.yandex.autotests.metrika.data.common.users.User;
import ru.yandex.autotests.metrika.data.parameters.visitors.VisitorCommentParameters;
import ru.yandex.autotests.metrika.data.parameters.visitors.VisitorInfoParameters;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.external.DelegateE;
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

@Features(Requirements.Feature.VISITORS)
@Stories({Requirements.Story.Visitors.COMMENTS})
@Title("Доступ к коментариям")
@RunWith(Parameterized.class)
public class CommentAccessTest {

    private static final String USER_ID_HASH = "1228125527";
    private static final String USER_ID_HASH_64 = "12885858787377372863";
    private static final String FIRST_VISIT_DATE = "2018-07-02";

    private static final User OWNER = METRIKA_TEST_COUNTERS;
    private static final User DELEGATE = USER_FOR_EMAIL_SUBSCRIPTION3;
    private static final User GUEST_EDIT = USER_FOR_EMAIL_SUBSCRIPTION2;

    private static UserSteps superUser;
    private static UserSteps owner;
    private static Long counterId;

    private UserSteps user;
    private String comment;

    @Parameter(0)
    public User userParam;

    @Parameter(1)
    public String title;

    @Parameters(name = "Пользователь: {0}, доступ: {1}")
    public static Collection<Object[]> createParameters() {
        return of(
                new Object[] {OWNER, "Владелец"},
                new Object[] {SUPPORT, "Саппорт"},
                new Object[] {SUPER_USER, "Суперпользователь"},
                new Object[] {DELEGATE, "Представитель"},
                new Object[] {GUEST_EDIT, "Пользователь с гостевым доступом на запись"}
        );
    }

    @BeforeClass
    public static void init() {
        superUser = new UserSteps().withUser(SUPER_USER);
    }

    @Before
    public void setup() {
        owner = new UserSteps().withUser(OWNER);
        counterId = Counters.MELDA_RU.getId();

        owner.onManagementSteps().onGrantsSteps().setGrantAndExpectSuccess(
                counterId,
                new GrantE().withPerm(GrantType.EDIT).withUserLogin(GUEST_EDIT.get(LOGIN)),
                ignoreQuota(true)
        );
        owner.onManagementSteps().onDelegatesSteps().addDelegateAndExpectSuccess(
                new DelegateE().withUserLogin(DELEGATE.get(LOGIN)),
                ignoreQuota(true)
        );
        user = new UserSteps().withUser(userParam);
        comment = RandomUtils.getString(10);
    }


    @Test
    public void addCommentTest() {
        user.onVisitorsSteps().addCommentAndExpectSuccess(new VisitorCommentParameters()
                .withComment(comment)
                .withId(counterId)
                .withUserIdHash(USER_ID_HASH)
                .withUserIdHash64(USER_ID_HASH_64)
                .withFirstVisitDate(FIRST_VISIT_DATE)
        );
    }

    @Test
    public void deleteCommentTest() {
        user.onVisitorsSteps().deleteCommentAndExpectSuccess(new VisitorInfoParameters()
                .withId(counterId)
                .withUserIdHash(USER_ID_HASH)
                .withUserIdHash64(USER_ID_HASH_64)
                .withFirstVisitDate(FIRST_VISIT_DATE)
        );
    }

    @After
    public void cleanUp() {
        superUser.onVisitorsSteps().deleteCommentAndExpectSuccess(new VisitorInfoParameters()
                .withId(counterId)
                .withUserIdHash(USER_ID_HASH)
                .withUserIdHash64(USER_ID_HASH_64)
                .withFirstVisitDate(FIRST_VISIT_DATE)
        );
        owner.onManagementSteps().onDelegatesSteps().deleteDelegateAndExpectSuccess(DELEGATE.get(LOGIN));
        owner.onManagementSteps().onGrantsSteps().deleteGrantAndExpectSuccess(counterId, GUEST_EDIT.get(LOGIN));
    }
}
