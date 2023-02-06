package ru.yandex.autotests.metrika.appmetrica.tests.ft.management.funnels;


import java.util.Collection;
import java.util.Collections;
import java.util.List;

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
import ru.yandex.autotests.metrika.appmetrica.wrappers.GrantWrapper;
import ru.yandex.metrika.api.management.client.external.GrantType;
import ru.yandex.metrika.mobmet.management.Application;
import ru.yandex.metrika.mobmet.model.Funnel;
import ru.yandex.metrika.mobmet.model.MobmetGrantE;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.appmetrica.data.Users.SIMPLE_USER;
import static ru.yandex.autotests.metrika.appmetrica.data.Users.SIMPLE_USER_2;
import static ru.yandex.autotests.metrika.appmetrica.matchers.ResponseMatchers.equivalentTo;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.GrantCreator.forUser;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.defaultFunnel;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.getDefaultApplication;


@Features(Requirements.Feature.Management.FUNNELS)
@Stories({
        Requirements.Story.Funnels.ADD,
        Requirements.Story.Funnels.LIST,
})
@Title("Просмотр воронки")
@RunWith(Parameterized.class)
public class GetFunnelTest {

    private static final User OWNER = Users.SIMPLE_USER;

    private final UserSteps ownerSteps = UserSteps.onTesting(OWNER);

    @Parameterized.Parameter
    public User funnelCreator;

    @Parameterized.Parameter(1)
    public User funnelViewer;

    @Parameterized.Parameter(2)
    public GrantWrapper grant;

    private UserSteps funnelViewerSteps;

    private Funnel expectedFunnel;

    private Long appId;

    private Long funnelId;

    @Parameterized.Parameters(name = "Создатель {0}. Пользователь {1}. {2}")
    public static Collection<Object[]> createParameters() {
        return ImmutableList.of(
                param(SIMPLE_USER, SIMPLE_USER, null),
                param(SIMPLE_USER, SIMPLE_USER_2, forUser(SIMPLE_USER_2).grant(GrantType.VIEW)),
                param(SIMPLE_USER, SIMPLE_USER_2, forUser(SIMPLE_USER_2).grant(GrantType.EDIT))
        );
    }

    @Before
    public void setup() {
        UserSteps funnelCreatorSteps = UserSteps.onTesting(funnelCreator);
        funnelViewerSteps = UserSteps.onTesting(funnelViewer);

        Application addedApplication = ownerSteps.onApplicationSteps().addApplication(getDefaultApplication());
        appId = addedApplication.getId();

        if (grant.getGrant() != null) {
            ownerSteps.onGrantSteps().createGrant(appId, grant);
        }

        Funnel funnelToAdd = defaultFunnel();
        expectedFunnel = funnelToAdd;
        funnelId = funnelCreatorSteps.onFunnelsSteps().addFunnel(appId, funnelToAdd).getId();
        expectedFunnel.withId(funnelId);
    }

    @Test
    public void getFunnel() {
        Funnel actualFunnel = funnelViewerSteps.onFunnelsSteps().getFunnel(appId, funnelId);
        assertThat("добавленная воронка эквивалентна ожидаемой", actualFunnel, equivalentTo(expectedFunnel));
    }

    @Test
    public void getFunnelList() {
        List<Funnel> funnels = funnelViewerSteps.onFunnelsSteps().getFunnelsList(appId);
        assertThat("список воронок содержит только добавленную воронку", funnels,
                equivalentTo(Collections.singletonList(expectedFunnel)));
    }

    @After
    public void teardown() {
        ownerSteps.onFunnelsSteps().deleteFunnelAndIgnoreResult(appId, funnelId);
        if (grant.getGrant() != null) {
            ownerSteps.onGrantSteps().deleteGrant(appId, grant.getGrant().getUserLogin());
        }
        ownerSteps.onApplicationSteps().deleteApplicationAndIgnoreResult(appId);
    }

    public static Object[] param(User funnelCreator, User funnelViewer, MobmetGrantE grant) {
        return new Object[]{funnelCreator, funnelViewer, new GrantWrapper(grant)};
    }
}
