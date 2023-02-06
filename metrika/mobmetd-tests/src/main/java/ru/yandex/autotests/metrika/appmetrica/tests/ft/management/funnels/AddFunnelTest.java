package ru.yandex.autotests.metrika.appmetrica.tests.ft.management.funnels;


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
import ru.yandex.autotests.metrika.appmetrica.wrappers.FunnelWrapper;
import ru.yandex.metrika.mobmet.management.Application;
import ru.yandex.metrika.mobmet.model.Funnel;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;
import java.util.List;

import static org.hamcrest.Matchers.hasItem;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.appmetrica.matchers.ResponseMatchers.equivalentTo;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.defaultFunnel;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.getDefaultApplication;

@Features(Requirements.Feature.Management.FUNNELS)
@Stories({
        Requirements.Story.Funnels.ADD,
        Requirements.Story.Funnels.LIST,
})
@Title("Добавление воронки")
@RunWith(Parameterized.class)
public class AddFunnelTest {

    private static final User OWNER = Users.SIMPLE_USER;

    private final UserSteps user = UserSteps.onTesting(OWNER);

    private Funnel expectedFunnel;

    private Long appId;

    private Funnel addedFunnel;

    @Parameterized.Parameter
    public FunnelWrapper funnelToAdd;

    @Parameterized.Parameters(name = "Funnel: {0}")
    public static Collection<Object[]> createParameters() {
        return ImmutableList.of(
                param(defaultFunnel()),
                param(defaultFunnel().withWindowInSeconds(1000L)),
                param(defaultFunnel()
                        .withPattern("cond(ym:uft, eventType=='EVENT_CLIENT') next " +
                                "cond(ym:uft, eventType=='EVENT_CLIENT' AND sessionType=='foreground')")
                        .withRestriction("eventType=='EVENT_CLIENT'"))
        );
    }

    @Before
    public void setup() {
        expectedFunnel = funnelToAdd.getFunnel();

        Application addedApplication = user.onApplicationSteps().addApplication(getDefaultApplication());
        appId = addedApplication.getId();
        addedFunnel = user.onFunnelsSteps().addFunnel(appId, funnelToAdd.getFunnel());
    }

    @Test
    public void addFunnel() {
        assertThat("добавленная воронка эквивалентна ожидаемой", addedFunnel, equivalentTo(expectedFunnel));
    }

    @Test
    public void funnelShouldBeInFunnelsList() {
        List<Funnel> funnels = user.onFunnelsSteps().getFunnelsList(appId);
        assertThat("список воронок содержит воронку, эквивалентную ожидаемой", funnels,
                hasItem(equivalentTo(expectedFunnel)));
    }

    @After
    public void teardown() {
        user.onFunnelsSteps().deleteFunnelAndIgnoreResult(appId, addedFunnel.getId());
        user.onApplicationSteps().deleteApplicationAndIgnoreResult(appId);
    }

    private static Object[] param(Funnel funnel) {
        return new Object[]{new FunnelWrapper(funnel)};
    }
}


