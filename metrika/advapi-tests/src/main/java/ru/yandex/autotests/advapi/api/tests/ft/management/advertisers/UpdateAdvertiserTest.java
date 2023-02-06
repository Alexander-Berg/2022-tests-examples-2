package ru.yandex.autotests.advapi.api.tests.ft.management.advertisers;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.advapi.V1ManagementAdvertiserAdvertiserIdPUTRequestSchema;
import ru.yandex.autotests.advapi.data.users.User;
import ru.yandex.autotests.advapi.steps.UserSteps;
import ru.yandex.autotests.irt.testutils.beandiffer2.comparestrategy.defaultcomparestrategy.DefaultCompareStrategy;
import ru.yandex.metrika.adv.api.management.advertiser.external.AdvertiserSettings;
import ru.yandex.metrika.api.management.client.counter.CounterIdEnhanced;
import ru.yandex.metrika.rbac.Permission;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Arrays;
import java.util.Collection;

import static java.util.Arrays.asList;
import static org.hamcrest.Matchers.*;
import static ru.yandex.autotests.advapi.api.tests.ft.management.AdvApiFeatures.MANAGEMENT;
import static ru.yandex.autotests.advapi.api.tests.ft.management.ManagementTestUtils.createSimpleAdvertiser;
import static ru.yandex.autotests.advapi.api.tests.ft.management.ManagementTestUtils.deleteGrantMultiplier;
import static ru.yandex.autotests.advapi.api.tests.ft.management.ManagementTestUtils.getAdvertiserSettings;
import static ru.yandex.autotests.advapi.api.tests.ft.management.ManagementTestUtils.getUpdateName;
import static ru.yandex.autotests.advapi.api.tests.ft.management.ManagementTestUtils.setGrantMultiplier;
import static ru.yandex.autotests.advapi.data.users.Users.SIMPLE_USER_1;
import static ru.yandex.autotests.advapi.data.users.Users.SIMPLE_USER_A;
import static ru.yandex.autotests.advapi.data.users.Users.SUPER_USER;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.irt.testutils.beandiffer2.BeanDifferMatcher.beanDiffer;
import static ru.yandex.autotests.irt.testutils.beandiffer2.beanfield.BeanFieldPath.newPath;
import static ru.yandex.autotests.irt.testutils.beandiffer2.comparestrategy.defaultcomparestrategy.DefaultCompareStrategies.onlyFields;

@Features(MANAGEMENT)
@Title("Изменение рекламодателя")
@RunWith(Parameterized.class)
public class UpdateAdvertiserTest {

    private static final User OWNER = SIMPLE_USER_1;
    private static final User GUEST = SIMPLE_USER_A;
    private static final User SUPER = SUPER_USER;

    private long advertiserId;
    private V1ManagementAdvertiserAdvertiserIdPUTRequestSchema body;

    @Parameterized.Parameter()
    public User otherUser;

    @Parameterized.Parameter(1)
    public AdvertiserSettings update;

    @Parameterized.Parameter(2)
    public DefaultCompareStrategy strategy;

    @Parameterized.Parameter(3)
    public String message;

    @Parameterized.Parameters(name = "{3}")
    public static Collection<Object[]> createParameters() {
        return asList(new Object[][]{
                {
                        OWNER,
                        getAdvertiserSettings(GUEST, Permission.VIEW, 17L, 35L).withName(getUpdateName("advertiser")),
                        onlyFields(newPath("name"), newPath("grants", "userLogin"), newPath("grants", "permission"), newPath("postClickDays"), newPath("postViewDays")),
                        "владелец может обновлять своих рекламодателей"
                },
                {
                        SUPER_USER,
                        getAdvertiserSettings(GUEST, Permission.VIEW, 27L, 45L).withName(getUpdateName("advertiser")),
                        onlyFields(newPath("name"), newPath("postClickDays"), newPath("postViewDays")),
                        "суперпользователь может обновлять чужих рекламодателей"
                },
                {
                        OWNER,
                        getAdvertiserSettings(GUEST, Permission.VIEW).withName(getUpdateName("advertiser")).withCounters(Arrays.asList(new CounterIdEnhanced().withCounterId(17L), new CounterIdEnhanced().withCounterId(20L))),
                        onlyFields(newPath("name")).forFields(newPath("counters")).useMatcher(allOf(iterableWithSize(2), hasItem(17L), hasItem(20L), not(hasItem(15L)))),
                        "владелец может изменить набор счетчиков"
                }
        });
    }

    @Before
    public void setUp() {
        advertiserId = createSimpleAdvertiser(OWNER).getAdvertiserId();

        setGrantMultiplier(SUPER, advertiserId, 2.0);

        body = new V1ManagementAdvertiserAdvertiserIdPUTRequestSchema().withAdvertiser(update);
    }

    @Test
    public void updateAdvertiser() {
        assertThat(message, UserSteps.withUser(otherUser).onAdvertisersSteps().updateAdvertiserAndExpectSuccess(advertiserId, body).getAdvertiser(), beanDiffer(update).useCompareStrategy(strategy));
    }

    @After
    public void cleanUp() {
        UserSteps.withUser(OWNER).onAdvertisersSteps().deleteAdvertiserAndExpectSuccess(advertiserId);
        deleteGrantMultiplier(SUPER, advertiserId);
    }
}
