package ru.yandex.autotests.internalapid.tests;

import org.hamcrest.Matchers;
import org.junit.*;
import ru.yandex.autotests.internalapid.beans.data.Counters;
import ru.yandex.autotests.internalapid.beans.data.User;
import ru.yandex.autotests.internalapid.beans.data.Users;
import ru.yandex.autotests.internalapid.util.DataUtil;
import ru.yandex.metrika.api.management.client.external.CounterFull;
import ru.yandex.metrika.api.management.client.external.GrantType;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Optional;

import static org.hamcrest.MatcherAssert.assertThat;
import static ru.yandex.autotests.internalapid.steps.IdmSteps.EXTERNAL_COUNTER_GRANT_ROLE;

@Title("Тест ручки /counter_access")
public class CounterAccessTest extends InternalApidTest {
    private static long COUNTER_ID;

    @BeforeClass
    public static void init() {
        COUNTER_ID = userSteps.onInternalApidSteps().createCounter(new CounterFull().withName(DataUtil.getRandomCounterName()).withSite("test.ru")).getId();
    }

    @AfterClass
    public static void teardown() {
        userSteps.onInternalApidSteps().deleteCounter(COUNTER_ID);
    }

    @Test
    @Title("У менеджера есть доступ к новому счетчику")
    public void managerHasAccessToNewCounter() {
        userSteps.onIdmSteps().addRole(Users.MANAGER.get(User.LOGIN), "manager", Users.MANAGER.get(User.LOGIN));
        testAccess(COUNTER_ID, Users.MANAGER, true);
    }

    @Test
    @Title("У обычного пользователя нет доступа к новому счетчику")
    public void simpleUserDoesntHaveAccessToNewCounter() {
        testAccess(COUNTER_ID, Users.METRIKA_INTAPI_AUTO, false);
    }

    @Test
    @Title("У yandexmanager пользователя нет доступа к новому счетчику")
    public void yandexManagerDoesntHaveAccessToNewCounter() {
        userSteps.onIdmSteps().addRole(Users.MANAGER.get(User.LOGIN), "yamanager", Users.MANAGER.get(User.LOGIN));
        testAccess(COUNTER_ID, Users.MANAGER, false);
    }

    @Test
    @Title("У yandexmanager пользователя есть доступ к счетчику Яндекса")
    public void yandexManagerHasAccessToYandexCounter() {
        userSteps.onIdmSteps().addRole(Users.MANAGER.get(User.LOGIN), "yamanager", Users.MANAGER.get(User.LOGIN));
        testAccess(Counters.METRIKA.getId(), Users.MANAGER, true);
    }

    @Test
    @Title("У пользователя с доступом на отдельный счетчик есть доступ")
    public void userWithAccessToSpecificCounterHasAccess() {
        userSteps.onIdmSteps().addRole(Users.MANAGER.get(User.LOGIN), EXTERNAL_COUNTER_GRANT_ROLE,
                Users.MANAGER.get(User.LOGIN), Optional.empty(), Optional.of(Counters.SIMPLE_COUNTER.getId()), Optional.of(GrantType.VIEW), Optional.of(false));
        testAccess(Counters.SIMPLE_COUNTER.getId(), Users.MANAGER, true);
    }

    @Before
    @After
    public void clean() {
        userSteps.onIdmSteps().removeRole(Users.MANAGER.get(User.LOGIN), "yamanager", Users.MANAGER.get(User.LOGIN));
        userSteps.onIdmSteps().removeRole(Users.MANAGER.get(User.LOGIN), "manager", Users.MANAGER.get(User.LOGIN));
        userSteps.onIdmSteps().removeRole(Users.MANAGER.get(User.LOGIN), EXTERNAL_COUNTER_GRANT_ROLE,
                Users.MANAGER.get(User.LOGIN), Optional.empty(), Optional.of(Counters.SIMPLE_COUNTER.getId()), Optional.of(GrantType.VIEW), Optional.of(false));
    }


    private void testAccess(long counterId, User manager, boolean b) {
        final String login = manager.get(User.LOGIN);
        boolean response = userSteps.onInternalApidSteps().getCounterAccess((int) counterId, login);
        assertThat(String.format("/counters_access вернул корректные данные для счетчика %s и логина %s", counterId, login), response, Matchers.is(b));
    }
}
