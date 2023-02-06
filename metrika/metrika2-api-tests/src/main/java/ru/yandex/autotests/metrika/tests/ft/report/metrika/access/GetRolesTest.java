package ru.yandex.autotests.metrika.tests.ft.report.metrika.access;

import com.google.common.collect.ImmutableSet;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.commons.junitparams.combinatorial.CombinatorialBuilder;
import ru.yandex.autotests.metrika.data.common.users.User;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.RolesResponse;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;
import java.util.Set;

import static com.google.common.collect.ImmutableList.of;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.hasItems;
import static ru.yandex.autotests.metrika.data.common.users.Users.*;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assumeThat;

@Features(Requirements.Feature.NDA)
@Stories({Requirements.Story.Report.Type.TABLE, Requirements.Story.Report.METADATA})
@Title("Получение роли")
@RunWith(Parameterized.class)
public class GetRolesTest {

    private static UserSteps user;

    @Parameterized.Parameter(0)
    public String title;

    @Parameterized.Parameter(1)
    public User currentUser;

    @Parameterized.Parameter(2)
    public Set<String> expectedRoles;

    @Parameterized.Parameter(3)
    public boolean hasInternalGrants;

    @Parameterized.Parameters(name = "Доступ: {0}, пользователь: {1}, роли: {2}, имеет доступ к внутреннему счетчику: {3}")
    public static Collection<Object[]> createParameters() {
        return CombinatorialBuilder.builder()
                .vectorValues(
                        of("суперпользователь", SUPER_USER, ImmutableSet.of("user", "super"), false),
                        of("менеджер", MANAGER, ImmutableSet.of("user", "manager"), false),
                        of("менеджер-яндекс", YAMANAGER, ImmutableSet.of("user", "yamanager"), false),
                        of("менеджер-директ", MANAGER_DIRECT, ImmutableSet.of("user", "manager_direct"), false),
                        of("пользователь с правом чтения счетчика idm", USER_WITH_IDM_VIEW_PERMISSION, ImmutableSet.of("user"), true),
                        of("пользователь с правом редактирования счетчика idm", USER_WITH_IDM_EDIT_PERMISSION, ImmutableSet.of("user"), true),
                        of("саппорт", SUPPORT, ImmutableSet.of("user", "support"), false),
                        of("обычный пользователь", SIMPLE_USER, ImmutableSet.of("user"), false))
                .build();
    }

    @Before
    public void setup() {
        user = new UserSteps().withDefaultAccuracy().withUser(currentUser);
    }

    @Test
    public void accessUserSuccess() {
        RolesResponse response = user.onInternalSteps().getRoles(null);

        assumeThat("верные роли", response.getRoles(), hasItems(expectedRoles.toArray()));
        assumeThat("верная информация о наличии гранта", response.getHasInternalCounterGrants(), equalTo(hasInternalGrants));
    }
}
