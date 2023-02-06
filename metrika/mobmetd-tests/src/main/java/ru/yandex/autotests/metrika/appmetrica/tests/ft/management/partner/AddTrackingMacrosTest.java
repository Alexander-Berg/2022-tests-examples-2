package ru.yandex.autotests.metrika.appmetrica.tests.ft.management.partner;

import java.util.List;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.autotests.metrika.appmetrica.wrappers.PartnerWrapper;
import ru.yandex.metrika.mobmet.model.redirect.TrackingPartner;
import ru.yandex.metrika.mobmet.model.redirect.TrackingPartnerMacros;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static org.hamcrest.Matchers.hasItem;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.appmetrica.data.Users.SIMPLE_USER;
import static ru.yandex.autotests.metrika.appmetrica.data.Users.SUPER_LIMITED;
import static ru.yandex.autotests.metrika.appmetrica.errors.ManagementError.FORBIDDEN;
import static ru.yandex.autotests.metrika.appmetrica.matchers.ResponseMatchers.equivalentTo;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.copy;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.defaultPartner;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.defaultTrackingMacros;

@Features(Requirements.Feature.Management.PARTNERS)
@Stories({
        Requirements.Story.Partner.ADD,
        Requirements.Story.Partner.LIST,
        Requirements.Story.Partner.INFO
})
@Title("Добавление макроса для интеграционного партнера")
public final class AddTrackingMacrosTest {

    private UserSteps supportUser = UserSteps.onTesting(SUPER_LIMITED);
    private UserSteps simpleUser = UserSteps.onTesting(SIMPLE_USER);

    private TrackingPartnerMacros expectedMacros;

    private TrackingPartner addedPartner;
    private TrackingPartnerMacros addedMacros;

    @Before
    public void setup() {
        addedPartner = supportUser.onPartnerSteps().createIntegratedPartner(PartnerWrapper.wrap(defaultPartner()));
        TrackingPartnerMacros macrosToAdd = defaultTrackingMacros()
                .withPartnerId(addedPartner.getId());
        expectedMacros = copy(macrosToAdd)
                .withPartnerId(addedPartner.getId());
        addedMacros = supportUser.onTrackingMacrosSteps().createTrackingMacros(macrosToAdd);
    }

    @Test
    public void checkAddedMacros() {
        assertThat("добавленный макрос эквивалентен ожидаемому", addedMacros,
                equivalentTo(expectedMacros));
    }

    @Test
    public void checkAddedMacrosInList() {
        List<TrackingPartnerMacros> templates = supportUser.onTrackingMacrosSteps()
                .getTrackingMacrosList(addedMacros.getPartnerId());
        assertThat("список макросов содержит макрос, эквивалентный ожидаемому",
                templates, hasItem(equivalentTo(expectedMacros)));
    }

    @Test
    public void checkSimpleCanNotCreateMacros() {
        simpleUser.onTrackingMacrosSteps()
                .createTrackingMacrosAndExpectError(defaultTrackingMacros(), FORBIDDEN);
    }

    @After
    public void teardown() {
        supportUser.onTrackingMacrosSteps().deleteMacrosIgnoringResult(addedMacros.getId());
        supportUser.onPartnerSteps().deletePartnerIgnoringResult(addedPartner.getId());
    }
}
