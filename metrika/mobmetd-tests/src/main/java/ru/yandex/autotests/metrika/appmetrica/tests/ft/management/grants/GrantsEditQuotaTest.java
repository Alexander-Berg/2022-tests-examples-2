package ru.yandex.autotests.metrika.appmetrica.tests.ft.management.grants;

import com.google.common.collect.ImmutableList;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.appmetrica.data.User;
import ru.yandex.autotests.metrika.appmetrica.data.Users;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData;
import ru.yandex.autotests.metrika.appmetrica.wrappers.GrantWrapper;
import ru.yandex.metrika.mobmet.management.Application;
import ru.yandex.metrika.mobmet.model.MobmetGrantE;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;
import java.util.function.Function;

import static org.apache.commons.lang3.ArrayUtils.toArray;
import static ru.yandex.autotests.metrika.appmetrica.data.User.LOGIN;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.GrantCreator.forUser;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.getDefaultApplication;
import static ru.yandex.metrika.api.management.client.external.GrantType.EDIT;
import static ru.yandex.metrika.api.management.client.external.GrantType.VIEW;

@Features(Requirements.Feature.Management.Application.GRANTS)
@Stories({
        Requirements.Story.Application.Grants.ADD,
        Requirements.Story.Application.Grants.QUOTA
})
@Title("Проверка отсутствия квот на редактирование доступов")
@RunWith(Parameterized.class)
public class GrantsEditQuotaTest {

    private static final int MAX_ATTEMPTS = 3;

    private static final User MANAGER = Users.SIMPLE_USER;

    private static final User GRANTEE = Users.SIMPLE_USER_2;

    private static final UserSteps managerSteps = UserSteps.onTesting(MANAGER);

    private static final TestData.GrantCreator GRANTS = forUser(GRANTEE);

    @Parameterized.Parameter()
    public GrantWrapper firstGrant;

    @Parameterized.Parameter(1)
    public GrantWrapper secondGrant;

    private GrantWrapper grantForUpdate;

    private Long appId;

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> createParameters() {
        return ImmutableList.<Object[]>builder()
                .add(param(GRANTS.grant(VIEW), GRANTS.grant(EDIT)))
                .add(param(GRANTS.grant(VIEW), GRANTS.getAgencyEditGrantToMultiplePartners()))
                .add(param(GRANTS.getAgencyEditGrantToMultiplePartners(), GRANTS.grant(VIEW)))
                .add(param(GRANTS.getAgencyViewGrantToMultiplePartnersAndEvents(), GRANTS.getAgencyViewGrantToMultiplePartnersAndEvents()))
                .build();
    }

    @Before
    public void setup() {
        Application addedApplication = managerSteps.onApplicationSteps().addApplication(getDefaultApplication());
        appId = addedApplication.getId();

        // чередуем права при редактировании
        Function<Integer, GrantWrapper> currentUpdate = i -> i % 2 == 0 ? firstGrant : secondGrant;
        managerSteps.onGrantSteps().createGrant(appId, firstGrant);
        int attempt = 1;
        for (; attempt < MAX_ATTEMPTS; ++attempt) {
            managerSteps.onGrantSteps().editGrant(appId, currentUpdate.apply(attempt));
        }
        grantForUpdate = currentUpdate.apply(attempt);
    }

    @Test
    public void edit() {
        managerSteps.onGrantSteps().editGrant(appId, grantForUpdate);
    }

    @After
    public void teardown() {
        managerSteps.onGrantSteps().deleteGrantIgnoringResult(appId, GRANTEE.get(LOGIN));
        managerSteps.onApplicationSteps().deleteApplicationAndIgnoreResult(appId);
    }

    private static Object[] param(MobmetGrantE firstGrant, MobmetGrantE secondGrant) {
        return toArray(new GrantWrapper(firstGrant), new GrantWrapper(secondGrant));
    }
}
