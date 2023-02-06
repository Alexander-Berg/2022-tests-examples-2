package ru.yandex.autotests.metrika.appmetrica.tests.ft.management.grants;

import com.google.common.collect.ImmutableList;
import com.google.common.collect.Sets;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.InternalRbacRolesGETSchema;
import ru.yandex.autotests.metrika.appmetrica.data.User;
import ru.yandex.autotests.metrika.appmetrica.data.Users;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;
import java.util.HashSet;
import java.util.Set;

import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.autotests.irt.testutils.allure.TestStepsEn.assumeThat;

@Features(Requirements.Feature.AUTH)
@Stories(Requirements.Story.AUTH)
@RunWith(Parameterized.class)
@Title("Проверка списка ролей пользователя")
public class RolesTest {

    @Parameterized.Parameter()
    public User user;

    @Parameterized.Parameter(1)
    public Set<String> expectedRoles;

    @Parameterized.Parameter(2)
    public boolean expectedHasInternalAppGrants;

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> createParameters() {
        return ImmutableList.<Object[]>builder()
                .add(param(Users.SUPER_LIMITED, Sets.newHashSet("api_read", "api_write", "appmetrica_support", "user"), false))
                .add(param(Users.SIMPLE_USER, Sets.newHashSet("api_read", "api_write", "user"), false))
                .build();
    }

    @Test
    public void test() {
        InternalRbacRolesGETSchema actual = UserSteps.onTesting(user).onGrantSteps().getRoles(user.get(User.LOGIN));
        assumeThat("Роли совпадают", new HashSet<>(actual.getRoles()), equalTo(expectedRoles));
        assertThat("Флаг внутренних доступов", actual.getHasInternalAppGrants(), equalTo(expectedHasInternalAppGrants));
    }

    public static Object[] param(User user, Set<String> roles, boolean hasInternalAppGrants) {
        return new Object[]{user, roles, hasInternalAppGrants};
    }
}
