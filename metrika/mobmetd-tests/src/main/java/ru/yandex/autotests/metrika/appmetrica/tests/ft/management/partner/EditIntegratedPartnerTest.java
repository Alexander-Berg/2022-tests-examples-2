package ru.yandex.autotests.metrika.appmetrica.tests.ft.management.partner;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.metrika.mobmet.model.redirect.TrackingPartner;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.appmetrica.data.Users.SIMPLE_USER;
import static ru.yandex.autotests.metrika.appmetrica.data.Users.SUPER_LIMITED;
import static ru.yandex.autotests.metrika.appmetrica.errors.ManagementError.FORBIDDEN;
import static ru.yandex.autotests.metrika.appmetrica.matchers.ResponseMatchers.equivalentTo;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.copy;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.defaultPartner;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.getPartnerName;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.randomUrlAddress;
import static ru.yandex.autotests.metrika.appmetrica.wrappers.PartnerWrapper.wrap;
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
@Title("Редактирование интеграционного партнера")
public final class EditIntegratedPartnerTest {

    private UserSteps supportUser = UserSteps.onTesting(SUPER_LIMITED);
    private UserSteps simpleUser = UserSteps.onTesting(SIMPLE_USER);

    private TrackingPartner expectedPartner;

    private TrackingPartner addedPartner;

    @Before
    public void setup() {
        TrackingPartner partnerToAdd = defaultPartner();
        partnerToAdd = copy(partnerToAdd).withType(ORDINARY);
        addedPartner = supportUser.onPartnerSteps().createIntegratedPartner(wrap(partnerToAdd));
        expectedPartner = copy(addedPartner)
                .withName(getPartnerName())
                .withIconUrl(randomUrlAddress());
    }

    @Test
    public void checkEditPartner() {
        TrackingPartner editedPartner = supportUser.onPartnerSteps().editIntegratedPartner(wrap(expectedPartner));
        assertThat("отредактированный партнер эквивалентен ожидаемому", editedPartner,
                equivalentTo(expectedPartner));
    }

    @Test
    public void checkSimpleCanNotEditIntegratedPartner() {
        simpleUser.onPartnerSteps()
                .editIntegratedPartnerAndExpectError(wrap(expectedPartner), FORBIDDEN);
    }

    @After
    public void teardown() {
        supportUser.onPartnerSteps().deletePartnerIgnoringResult(addedPartner.getId());
    }
}
