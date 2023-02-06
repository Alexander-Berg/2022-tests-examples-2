package ru.yandex.autotests.metrika.appmetrica.tests.ft.management.funnels;

import java.util.List;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import ru.yandex.autotests.metrika.appmetrica.data.User;
import ru.yandex.autotests.metrika.appmetrica.data.Users;
import ru.yandex.autotests.metrika.appmetrica.errors.ManagementError;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.autotests.metrika.appmetrica.wrappers.GrantWrapper;
import ru.yandex.metrika.api.management.client.external.GrantType;
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
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.GrantCreator.forUser;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.defaultFunnel;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.editFunnel;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.getDefaultApplication;

@Features(Requirements.Feature.Management.FUNNELS)
@Stories({
        Requirements.Story.Funnels.ADD,
        Requirements.Story.Funnels.EDIT,
        Requirements.Story.Funnels.DELETE,
        Requirements.Story.Funnels.LIST
})
@Title("Использование воронки с view-доступом на приложение")
public class ViewPermFunnelTest {

    private static final User APP_OWNER = Users.SIMPLE_USER;
    private static final User APP_VIEWER = Users.SIMPLE_USER_2;

    private static final UserSteps appOwner = UserSteps.onTesting(APP_OWNER);
    private static final UserSteps appViewer = UserSteps.onTesting(APP_VIEWER);

    private Long appId;

    private Funnel addedFunnel;

    private GrantWrapper addedViewGrant;

    @Before
    public void setup() {
        Application addedApplication = appOwner.onApplicationSteps().addApplication(getDefaultApplication());
        appId = addedApplication.getId();

        GrantWrapper viewGrant = new GrantWrapper(forUser(APP_VIEWER).grant(GrantType.VIEW));
        addedViewGrant = new GrantWrapper(appOwner.onGrantSteps().createGrant(appId, viewGrant));
    }

    @Test
    @Title("Пользователь с доступом на чтение может добавить воронку")
    public void checkViewerCanAddFunnel() {
        Funnel funnelToAdd = defaultFunnel();
        addedFunnel = appViewer.onFunnelsSteps().addFunnel(appId, funnelToAdd);
        assumeThat("добавленная воронка эквивалентна ожидаемой", addedFunnel, equivalentTo(funnelToAdd));

        List<Funnel> viewerFunnels = appViewer.onFunnelsSteps().getFunnelsList(appId);
        assertThat("список воронок содержит воронку, эквивалентную ожидаемой", viewerFunnels,
                hasItem(equivalentTo(addedFunnel)));
    }

    @Test
    @Title("Пользователь с доступом на чтение может обновить свою воронку")
    public void checkViewerCanEditOwnFunnel() {
        Funnel funnelToAdd = defaultFunnel();
        addedFunnel = appViewer.onFunnelsSteps().addFunnel(appId, funnelToAdd);
        assumeThat("добавленная воронка эквивалентна ожидаемой", addedFunnel, equivalentTo(funnelToAdd));

        Funnel newFunnelValue = editFunnel(addedFunnel);
        Funnel actualFunnel = appViewer.onFunnelsSteps().updateFunnel(appId, newFunnelValue.getId(), newFunnelValue);
        assertThat("обновлённая воронка эквивалентна ожидаемой", actualFunnel, equivalentTo(newFunnelValue));
    }

    @Test
    @Title("Пользователь с доступом на чтение может удалить свою воронку")
    public void checkViewerCanDeleteItsFunnel() {
        Funnel funnelToAdd = defaultFunnel();
        addedFunnel = appViewer.onFunnelsSteps().addFunnel(appId, funnelToAdd);
        assumeThat("добавленная воронка эквивалентна ожидаемой", addedFunnel, equivalentTo(funnelToAdd));

        appViewer.onFunnelsSteps().deleteFunnel(appId, addedFunnel.getId());
        List<Funnel> funnels = appViewer.onFunnelsSteps().getFunnelsList(appId);
        assertThat("список воронок не содержит воронку, эквивалентную ожидаемой", funnels,
                not(hasItem(equivalentTo(addedFunnel))));
    }

    @Test
    @Title("Пользователь с доступом на чтение не может редактировать чужую воронку")
    public void checkViewerCantEditOwnersFunnel() {
        Funnel funnelToAdd = defaultFunnel();
        addedFunnel = appOwner.onFunnelsSteps().addFunnel(appId, funnelToAdd);
        assumeThat("добавленная воронка эквивалентна ожидаемой", addedFunnel, equivalentTo(funnelToAdd));

        Funnel newFunnelValue = editFunnel(addedFunnel);
        appViewer.onFunnelsSteps().updateFunnelAndExpectError(
                appId, newFunnelValue.getId(), newFunnelValue, ManagementError.FORBIDDEN);
    }

    @Test
    @Title("Пользователь с доступом на чтение не может удалить чужую воронку")
    public void checkViewerCantDeleteOwnersFunnel() {
        Funnel funnelToAdd = defaultFunnel();
        addedFunnel = appOwner.onFunnelsSteps().addFunnel(appId, funnelToAdd);
        assumeThat("добавленная воронка эквивалентна ожидаемой", addedFunnel, equivalentTo(funnelToAdd));

        appViewer.onFunnelsSteps().deleteFunnelAndExpectError(appId, addedFunnel.getId(), ManagementError.FORBIDDEN);
    }

    @After
    public void teardown() {
        appOwner.onFunnelsSteps().deleteFunnelAndIgnoreResult(appId, addedFunnel.getId());
        appOwner.onGrantSteps().deleteGrantIgnoringResult(appId, addedViewGrant);
        appOwner.onApplicationSteps().deleteApplicationAndIgnoreResult(appId);
    }
}
