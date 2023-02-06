package ru.yandex.autotests.metrika.appmetrica.tests.ft.management.partner;

import java.util.Collection;
import java.util.List;

import com.google.common.collect.ImmutableList;
import org.apache.commons.lang3.ArrayUtils;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.appmetrica.actions.EditAction;
import ru.yandex.autotests.metrika.appmetrica.data.User;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.autotests.metrika.appmetrica.wrappers.GrantWrapper;
import ru.yandex.autotests.metrika.appmetrica.wrappers.PartnerWrapper;
import ru.yandex.metrika.mobmet.management.Application;
import ru.yandex.metrika.mobmet.model.MobmetGrantE;
import ru.yandex.metrika.mobmet.model.redirect.TrackingPartner;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static org.hamcrest.core.IsCollectionContaining.hasItem;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.appmetrica.data.Users.SIMPLE_USER;
import static ru.yandex.autotests.metrika.appmetrica.matchers.ResponseMatchers.equivalentTo;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.changePartnerName;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.defaultPartner;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.getDefaultApplication;
import static ru.yandex.autotests.metrika.appmetrica.wrappers.PartnerWrapper.wrap;

/**
 * Created by graev on 21/12/2016.
 */
@Features(Requirements.Feature.Management.PARTNERS)
@Stories({
        Requirements.Story.Partner.EDIT
})
@RunWith(Parameterized.class)
@Title("Редактирование партнера")
public final class EditPartnerTest {

    @Parameterized.Parameter
    public User owner;

    @Parameterized.Parameter(1)
    public User user;

    @Parameterized.Parameter(2)
    public GrantWrapper grant;

    @Parameterized.Parameter(3)
    public PartnerWrapper partnerToAdd;

    @Parameterized.Parameter(4)
    public EditAction<TrackingPartner, TrackingPartner> editAction;

    private UserSteps ownerSteps;

    private UserSteps userSteps;

    private Long appId;

    private Long partnerId;

    private TrackingPartner editedPartner;

    private TrackingPartner expectedPartner;

    @Parameterized.Parameters(name = "Создатель {0}. Пользователь {1}. {2}. {3}. {4}")
    public static Collection<Object[]> createParameters() {
        return ImmutableList.of(
                param(SIMPLE_USER, SIMPLE_USER)
        );
    }

    @Before
    public void setup() {
        ownerSteps = UserSteps.onTesting(owner);
        userSteps = UserSteps.onTesting(user);

        TrackingPartner addedPartner = ownerSteps.onPartnerSteps().createPartner(partnerToAdd);
        partnerId = addedPartner.getId();

        final Application addedApplication = ownerSteps.onApplicationSteps().addApplication(getDefaultApplication());
        appId = addedApplication.getId();

        ownerSteps.onGrantSteps().createGrantIfAny(appId, grant, partnerId);

        expectedPartner = editAction.edit(addedPartner);
        editedPartner = userSteps.onPartnerSteps().editPartner(wrap(editAction.getUpdate(addedPartner)));
    }

    @Test
    public void checkPartnerInfo() {
        assertThat("отредактированный партнер эквивалентен ожидаемому", editedPartner,
                equivalentTo(expectedPartner));
    }

    @Test
    public void checkActualPartnerInfo() {
        final TrackingPartner actual = userSteps.onPartnerSteps().getPartner(partnerId);
        assertThat("актуальный партнер эквивалентен ожидаемому", actual,
                equivalentTo(expectedPartner));
    }

    @Test
    public void checkPartnersList() {
        final List<TrackingPartner> list = userSteps.onPartnerSteps().getPartnersList();
        assertThat("список партнеров содержит партнера, эквивалентного ожидаемому", list,
                hasItem(equivalentTo(expectedPartner)));
    }

    @After
    public void teardown() {
        ownerSteps.onPartnerSteps().deletePartnerIgnoringResult(partnerId);
        ownerSteps.onGrantSteps().deleteGrantIgnoringResult(appId, grant);
        ownerSteps.onApplicationSteps().deleteApplicationAndIgnoreResult(appId);
    }

    private static Object[] param(User owner, User user) {
        return param(owner, user, null, defaultPartner(), changePartnerName());
    }

    private static Object[] param(User owner, User user, MobmetGrantE grant, TrackingPartner partner,
                                  EditAction<TrackingPartner, TrackingPartner> editAction) {
        return ArrayUtils.toArray(owner, user, new GrantWrapper(grant), new PartnerWrapper(partner), editAction);
    }
}
