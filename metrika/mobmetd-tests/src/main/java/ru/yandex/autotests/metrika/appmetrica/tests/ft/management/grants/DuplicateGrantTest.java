package ru.yandex.autotests.metrika.appmetrica.tests.ft.management.grants;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.junit.runners.Parameterized.Parameter;
import ru.yandex.autotests.metrika.appmetrica.data.User;
import ru.yandex.autotests.metrika.appmetrica.data.Users;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData;
import ru.yandex.autotests.metrika.appmetrica.wrappers.GrantWrapper;
import ru.yandex.autotests.metrika.commons.junitparams.combinatorial.CombinatorialBuilder;
import ru.yandex.metrika.api.management.client.external.GrantType;
import ru.yandex.metrika.mobmet.management.Application;
import ru.yandex.metrika.mobmet.model.MobmetGrantE;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;
import java.util.function.Supplier;

import static java.util.Arrays.asList;
import static java.util.stream.Collectors.toList;
import static org.apache.commons.lang3.ArrayUtils.toArray;
import static ru.yandex.autotests.metrika.appmetrica.errors.ManagementError.GRANT_DUPLICATE;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.GrantCreator.forUser;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.getDefaultApplication;
import static ru.yandex.metrika.api.management.client.external.GrantType.EDIT;
import static ru.yandex.metrika.api.management.client.external.GrantType.VIEW;

/**
 * Проверяем, что нельзя дать пользователю два разных доступа MOBMET-6532.
 */
@Features(Requirements.Feature.Management.Application.GRANTS)
@Stories({
        Requirements.Story.Application.Grants.ADD,
        Requirements.Story.Application.Grants.LIST,
        Requirements.Story.Application.Grants.INFO,
})
@Title("Задвоение доступа")
@RunWith(Parameterized.class)
public final class DuplicateGrantTest {

    private static final User MANAGER = Users.SIMPLE_USER;

    private static final User GRANTEE = Users.SIMPLE_USER_2;

    private static final UserSteps managerSteps = UserSteps.onTesting(MANAGER);

    private static final TestData.GrantCreator GRANTS = forUser(GRANTEE);

    @Parameter()
    public GrantType firstGrantToAddType;

    @Parameter(1)
    public GrantWrapper firstGrantToAdd;

    @Parameter(2)
    public GrantType secondGrantToAddType;

    @Parameter(3)
    public GrantWrapper secondGrantToAdd;

    @Parameter(4)
    public UserLoginType userLoginType;

    private Long appId;

    @Parameterized.Parameters(name = "First: {0}; second: {2}; login type: {4}")
    public static Collection<Object[]> createParameters() {
        Collection<Supplier<MobmetGrantE>> grants = asList(
                () -> GRANTS.grant(VIEW),
                () -> GRANTS.grant(EDIT),
                GRANTS::agencyViewGrant,
                GRANTS::agencyEditGrant
        );

        return CombinatorialBuilder.builder()
                .values(grants)
                .values(grants)
                .values(UserLoginType.values())
                .build().stream()
                .map(params -> {
                    @SuppressWarnings("unchecked")
                    MobmetGrantE firstGrant = ((Supplier<MobmetGrantE>) params[0]).get();
                    @SuppressWarnings("unchecked")
                    MobmetGrantE secondGrant = ((Supplier<MobmetGrantE>) params[1]).get();
                    UserLoginType userLoginType = (UserLoginType) params[2];

                    return param(firstGrant, secondGrant, userLoginType);
                })
                .collect(toList());
    }

    @Before
    public void setup() {
        Application addedApplication = managerSteps.onApplicationSteps().addApplication(getDefaultApplication());
        appId = addedApplication.getId();
    }

    @Test
    public void checkErrorOnDuplicate() {
        managerSteps.onGrantSteps().createGrant(appId, firstGrantToAdd);
        managerSteps.onGrantSteps().createGrantAndExpectError(appId, secondGrantToAdd, GRANT_DUPLICATE);
    }

    @After
    public void teardown() {
        managerSteps.onGrantSteps().deleteGrantIgnoringResult(appId, firstGrantToAdd);
        managerSteps.onGrantSteps().deleteGrantIgnoringResult(appId, secondGrantToAdd);
        managerSteps.onApplicationSteps().deleteApplicationAndIgnoreResult(appId);
    }

    private static Object[] param(MobmetGrantE firstGrant, MobmetGrantE secondGrant, UserLoginType userLoginType) {
        if (userLoginType == UserLoginType.EMAIL) {
            firstGrant.withUserLogin(firstGrant.getUserLogin() + "@yandex.ru");
            secondGrant.withUserLogin(secondGrant.getUserLogin() + "@yandex.ru");
        }

        return toArray(
                firstGrant.getPerm(), new GrantWrapper(firstGrant),
                secondGrant.getPerm(), new GrantWrapper(secondGrant),
                userLoginType
        );
    }

    private enum UserLoginType {
        LOGIN,
        EMAIL
    }

}
