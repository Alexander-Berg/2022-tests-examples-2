package ru.yandex.autotests.metrika.appmetrica.tests.ft.management.partner;


import java.util.Collection;
import java.util.List;

import com.google.common.collect.ImmutableList;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.appmetrica.data.Partner;
import ru.yandex.autotests.metrika.appmetrica.data.Partners;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.autotests.metrika.appmetrica.wrappers.PartnerWrapper;
import ru.yandex.metrika.mobmet.model.redirect.TrackingPartner;
import ru.yandex.metrika.segments.apps.misc.PartnerType;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static org.apache.commons.lang3.ArrayUtils.toArray;
import static org.hamcrest.core.IsCollectionContaining.hasItem;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.appmetrica.data.Users.SIMPLE_USER;
import static ru.yandex.autotests.metrika.appmetrica.matchers.ResponseMatchers.equivalentTo;

@Features(Requirements.Feature.Management.PARTNERS)
@Stories({
        Requirements.Story.Partner.INFO,
        Requirements.Story.Partner.LIST
})
@Title("Информация о специальных партнерах")
@RunWith(Parameterized.class)
public class GetSpecialPartnerTest {

    private static final UserSteps OWNER = UserSteps.onTesting(SIMPLE_USER);

    @Parameterized.Parameter
    public PartnerWrapper expectedSpecialPartner;

    @Parameterized.Parameters(name = "Партнёр {0}")
    public static Collection<Object[]> createParameters() {
        return ImmutableList.of(
                // У Facebook сейчас чехарда с правами. Раскомментировать, когда всё нормализуется
                //param(Partners.FACEBOOK, PartnerType.FACEBOOK, "Facebook"),
                param(Partners.ADWORDS, PartnerType.ADWORDS, "Google Ads"),
                param(Partners.MYTARGET, PartnerType.MYTARGET, "MyTarget"),
                param(Partners.DOUBLECLICK, PartnerType.DOUBLECLICK, "DoubleClick")
        );
    }

    @Test
    public void checkSinglePartner() {
        TrackingPartner actual = OWNER.onPartnerSteps().getPartner(expectedSpecialPartner.getPartner().getId());
        assertThat("актуальный партнер эквивалентен ожидаемому", actual,
                equivalentTo(expectedSpecialPartner.getPartner()));
    }

    @Test
    public void checkPartnersList() {
        final List<TrackingPartner> list = OWNER.onPartnerSteps().getPartnersList();
        assertThat("список партнеров содержит партнера, эквивалентного ожидаемому", list,
                hasItem(equivalentTo(expectedSpecialPartner.getPartner())));
    }

    private static Object[] param(Partner partner, PartnerType partnerType, String name) {
        return toArray(new PartnerWrapper(
                // проверяем только базовые поля
                new TrackingPartner().withId(partner.get(Partner.ID)).withType(partnerType).withName(name)));
    }
}
