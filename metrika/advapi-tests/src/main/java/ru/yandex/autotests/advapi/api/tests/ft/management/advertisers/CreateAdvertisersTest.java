package ru.yandex.autotests.advapi.api.tests.ft.management.advertisers;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import ru.yandex.autotests.advapi.api.tests.ft.management.ManagementTestUtils;
import ru.yandex.autotests.advapi.data.users.User;
import ru.yandex.autotests.advapi.steps.UserSteps;
import ru.yandex.autotests.irt.testutils.beandiffer2.comparestrategy.CompareStrategy;
import ru.yandex.metrika.adv.api.management.advertiser.external.AdvertiserSettings;
import ru.yandex.metrika.rbac.Permission;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Title;

import static org.hamcrest.Matchers.containsInAnyOrder;
import static ru.yandex.autotests.advapi.api.tests.ft.management.AdvApiFeatures.MANAGEMENT;
import static ru.yandex.autotests.advapi.api.tests.ft.management.ManagementTestUtils.getAdvertiserSettings;
import static ru.yandex.autotests.advapi.data.users.Users.SIMPLE_USER_1;
import static ru.yandex.autotests.advapi.data.users.Users.SIMPLE_USER_A;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.irt.testutils.beandiffer2.BeanDifferMatcher.beanDiffer;
import static ru.yandex.autotests.irt.testutils.beandiffer2.beanfield.BeanFieldPath.newPath;
import static ru.yandex.autotests.irt.testutils.beandiffer2.comparestrategy.defaultcomparestrategy.DefaultCompareStrategies.onlyFields;

@Features(MANAGEMENT)
@Title("Создания рекламодателя")
public class CreateAdvertisersTest {

    private static final long POST_CLICK_DAYS = 1L;
    private static final long POST_VIEW_DAYS = 1L;
    private static final User OWNER = SIMPLE_USER_A;
    private static final User GUEST = SIMPLE_USER_1;

    private AdvertiserSettings settings;
    private AdvertiserSettings advertiser;

    @Before
    public void setUp() {
        settings = getAdvertiserSettings(GUEST, Permission.VIEW, POST_CLICK_DAYS, POST_VIEW_DAYS);
        advertiser = ManagementTestUtils.createAdvertiser(OWNER, settings);
    }

    @Test
    @Title("Создание рекламодателя")
    public void createAdvertiser() {
        CompareStrategy strategy = onlyFields(
                newPath("name"),
                newPath("owner"),
                newPath("grants", "userLogin"),
                newPath("grants", "permission"),
                newPath("postClickDays"),
                newPath("postViewDays"))
                .forFields(newPath("counters")).useMatcher(containsInAnyOrder(advertiser.getCounters()));

        assertThat("рекламодатель создан", advertiser, beanDiffer(settings.withOwner(OWNER.toString())).useCompareStrategy(strategy));
    }

    @After
    public void cleanUp() {
        UserSteps.withUser(OWNER).onAdvertisersSteps().deleteAdvertiserAndExpectSuccess(advertiser.getAdvertiserId());
    }
}
