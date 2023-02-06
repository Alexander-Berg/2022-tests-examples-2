package ru.yandex.autotests.metrika.appmetrica.tests.ft.management.partner;

import java.util.Collection;
import java.util.List;

import com.google.common.collect.ImmutableList;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
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

import static org.apache.commons.lang3.ArrayUtils.toArray;
import static org.hamcrest.core.IsCollectionContaining.hasItem;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.appmetrica.data.Users.SIMPLE_USER;
import static ru.yandex.autotests.metrika.appmetrica.data.Users.SIMPLE_USER_2;
import static ru.yandex.autotests.metrika.appmetrica.matchers.ResponseMatchers.equivalentTo;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.GrantCreator;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.GrantCreator.forUser;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.copy;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.defaultPartner;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.getDefaultApplication;
import static ru.yandex.autotests.metrika.appmetrica.wrappers.PartnerWrapper.wrap;
import static ru.yandex.metrika.api.management.client.external.GrantType.AGENCY_EDIT;
import static ru.yandex.metrika.api.management.client.external.GrantType.AGENCY_VIEW;
import static ru.yandex.metrika.api.management.client.external.GrantType.EDIT;
import static ru.yandex.metrika.api.management.client.external.GrantType.VIEW;
import static ru.yandex.metrika.segments.apps.misc.PartnerType.ORDINARY;

/**
 * Created by graev on 21/12/2016.
 */
@Features(Requirements.Feature.Management.PARTNERS)
@Stories({
        Requirements.Story.Partner.ADD,
        Requirements.Story.Partner.LIST,
        Requirements.Story.Partner.INFO
})
@Title("Добавление партнера")
@RunWith(Parameterized.class)
public final class AddPartnerTest {

    private static final GrantCreator GRANTS = forUser(SIMPLE_USER);

    @Parameterized.Parameter
    public User owner;

    @Parameterized.Parameter(1)
    public User user;

    @Parameterized.Parameter(2)
    public GrantWrapper grant;

    @Parameterized.Parameter(3)
    public PartnerWrapper partnerToAdd;

    @Parameterized.Parameter(4)
    public TrackingPartner expectedPartner;

    private UserSteps ownerSteps;

    private UserSteps userSteps;

    private TrackingPartner addedPartner;

    private Long parnterId;

    private Long appId;

    @Parameterized.Parameters(name = "Создатель {0}. Пользователь {1}. {2}. {3}")
    public static Collection<Object[]> createParameters() {
        return ImmutableList.of(
                param(SIMPLE_USER, SIMPLE_USER),
                param(SIMPLE_USER_2, SIMPLE_USER, GRANTS.grant(VIEW)),
                param(SIMPLE_USER_2, SIMPLE_USER, GRANTS.grant(EDIT)),
                param(SIMPLE_USER_2, SIMPLE_USER, GRANTS.grant(AGENCY_VIEW)),
                param(SIMPLE_USER_2, SIMPLE_USER, GRANTS.grant(AGENCY_EDIT))
        );
    }

    @Before
    public void setup() {
        ownerSteps = UserSteps.onTesting(owner);
        userSteps = UserSteps.onTesting(user);

        addedPartner = ownerSteps.onPartnerSteps().createPartner(partnerToAdd);
        parnterId = addedPartner.getId();

        final Application addedApplication = ownerSteps.onApplicationSteps().addApplication(getDefaultApplication());
        appId = addedApplication.getId();

        ownerSteps.onGrantSteps().createGrantIfAny(appId, grant, parnterId);
    }

    @Test
    public void checkPartnerInfo() {
        assertThat("добавленный партнер эквивалентен ожидаемому", addedPartner,
                equivalentTo(expectedPartner));
    }

    @Test
    public void checkActualPartnerInfo() {
        final TrackingPartner actual = userSteps.onPartnerSteps().getPartner(parnterId);
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
        ownerSteps.onPartnerSteps().deletePartnerIgnoringResult(addedPartner.getId());
        ownerSteps.onGrantSteps().deleteGrantIgnoringResult(appId, grant);
        ownerSteps.onApplicationSteps().deleteApplicationAndIgnoreResult(appId);
    }

    private static Object[] param(User owner, User user) {
        return param(owner, user, null);
    }

    private static Object[] param(User owner, User user, MobmetGrantE grant) {
        return param(owner, user, grant, defaultPartner());
    }

    private static Object[] param(User owner, User user, MobmetGrantE grant, TrackingPartner partner) {
        return toArray(owner, user, new GrantWrapper(grant), wrap(partner), copy(partner).withType(ORDINARY));
    }
}
