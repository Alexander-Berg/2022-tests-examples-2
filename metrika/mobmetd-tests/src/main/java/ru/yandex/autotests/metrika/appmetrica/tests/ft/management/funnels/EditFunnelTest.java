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

import static org.hamcrest.Matchers.hasItem;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.appmetrica.matchers.ResponseMatchers.equivalentTo;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.defaultFunnel;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.editFunnel;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.getDefaultApplication;


@Features(Requirements.Feature.Management.FUNNELS)
@Stories({
        Requirements.Story.Funnels.ADD,
        Requirements.Story.Funnels.EDIT,
        Requirements.Story.Funnels.LIST,
})
@Title("Редактирование воронки")
public class EditFunnelTest {

    private static final User OWNER = Users.SIMPLE_USER;

    private final UserSteps user = UserSteps.onTesting(OWNER);

    private Funnel actualFunnel;

    private Funnel newFunnelValue;

    private Long appId;

    private Long funnelId;

    @Before
    public void setup() {
        Funnel funnelToAdd = defaultFunnel();

        Application addedApplication = user.onApplicationSteps().addApplication(getDefaultApplication());
        appId = addedApplication.getId();
        Funnel addedFunnel = user.onFunnelsSteps().addFunnel(appId, funnelToAdd);
        funnelId = addedFunnel.getId();

        newFunnelValue = editFunnel(addedFunnel);
        actualFunnel = user.onFunnelsSteps().updateFunnel(appId, funnelId, newFunnelValue);
    }

    @Test
    public void addFunnel() {
        assertThat("обновлённая воронка эквивалентна ожидаемой", actualFunnel, equivalentTo(newFunnelValue));
    }

    @Test
    public void segmentShouldBeInFunnelsList() {
        final List<Funnel> segments = user.onFunnelsSteps().getFunnelsList(appId);
        assertThat("список воронок содержит воронку, эквивалентную ожидаемой", segments,
                hasItem(equivalentTo(newFunnelValue)));
    }

    @After
    public void teardown() {
        user.onFunnelsSteps().deleteFunnelAndIgnoreResult(appId, funnelId);
        user.onApplicationSteps().deleteApplicationAndIgnoreResult(appId);
    }
}
