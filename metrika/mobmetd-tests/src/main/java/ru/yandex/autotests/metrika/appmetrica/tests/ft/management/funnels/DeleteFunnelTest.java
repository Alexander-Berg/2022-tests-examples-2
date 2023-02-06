package ru.yandex.autotests.metrika.appmetrica.tests.ft.management.funnels;

import java.util.List;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import ru.yandex.autotests.metrika.appmetrica.data.User;
import ru.yandex.autotests.metrika.appmetrica.data.Users;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.metrika.mobmet.management.Application;
import ru.yandex.metrika.mobmet.model.Funnel;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static org.hamcrest.CoreMatchers.not;
import static org.hamcrest.Matchers.hasItem;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assumeThat;
import static ru.yandex.autotests.metrika.appmetrica.matchers.ResponseMatchers.equivalentTo;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.defaultFunnel;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.getDefaultApplication;

@Features(Requirements.Feature.Management.FUNNELS)
@Stories({
        Requirements.Story.Funnels.DELETE,
        Requirements.Story.Funnels.LIST,
})
@Title("Удаление воронки")
public class DeleteFunnelTest {

    private static final User OWNER = Users.SIMPLE_USER;

    private final UserSteps user = UserSteps.onTesting(OWNER);

    private Funnel expectedFunnel;

    private Long appId;

    private Funnel addedFunnel;

    @Before
    public void setup() {
        Funnel funnelToAdd = defaultFunnel();
        expectedFunnel = funnelToAdd;

        Application addedApplication = user.onApplicationSteps().addApplication(getDefaultApplication());
        appId = addedApplication.getId();
        addedFunnel = user.onFunnelsSteps().addFunnel(appId, funnelToAdd);
        assumeThat("добавленная воронка эквивалентна ожидаемомой", addedFunnel, equivalentTo(expectedFunnel));

        user.onFunnelsSteps().deleteFunnel(appId, addedFunnel.getId());
    }

    @Test
    public void funnelShouldNotBeInFunnelsList() {
        List<Funnel> funnels = user.onFunnelsSteps().getFunnelsList(appId);
        assertThat("список воронок не содержит воронку, эквивалентную ожидаемой", funnels,
                not(hasItem(equivalentTo(expectedFunnel))));
    }

    @After
    public void teardown() {
        user.onFunnelsSteps().deleteFunnelAndIgnoreResult(appId, addedFunnel.getId());
        user.onApplicationSteps().deleteApplicationAndIgnoreResult(appId);
    }
}
