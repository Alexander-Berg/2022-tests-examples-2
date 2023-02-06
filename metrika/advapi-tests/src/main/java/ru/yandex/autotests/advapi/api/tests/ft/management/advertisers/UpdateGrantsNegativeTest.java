package ru.yandex.autotests.advapi.api.tests.ft.management.advertisers;

import java.util.List;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;

import ru.yandex.advapi.V1ManagementAdvertiserAdvertiserIdPUTSchema;
import ru.yandex.autotests.advapi.data.users.User;
import ru.yandex.autotests.advapi.steps.UserSteps;
import ru.yandex.autotests.irt.testutils.allure.AssumptionException;
import ru.yandex.autotests.irt.testutils.allure.TestSteps;
import ru.yandex.metrika.adv.api.management.advertiser.external.AdvertiserSettings;
import ru.yandex.metrika.api.management.client.grants.Grant;
import ru.yandex.metrika.rbac.Permission;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Title;

import static java.util.Collections.emptyList;
import static java.util.Collections.singletonList;
import static ru.yandex.autotests.advapi.Errors.QUOTA_EXCEEDED;
import static ru.yandex.autotests.advapi.api.tests.ft.management.AdvApiFeatures.MANAGEMENT;
import static ru.yandex.autotests.advapi.api.tests.ft.management.ManagementTestUtils.createSimpleAdvertiser;
import static ru.yandex.autotests.advapi.api.tests.ft.management.ManagementTestUtils.setGrantMultiplier;
import static ru.yandex.autotests.advapi.api.tests.ft.management.ManagementTestUtils.deleteGrantMultiplier;
import static ru.yandex.autotests.advapi.data.users.Users.READ_GUEST;
import static ru.yandex.autotests.advapi.data.users.Users.SIMPLE_USER_1;
import static ru.yandex.autotests.advapi.data.users.Users.SUPER_USER;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.ERROR_MESSAGE;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.expectError;

@Features(MANAGEMENT)
@Title("Изменение доступов (негативные)")
public class UpdateGrantsNegativeTest {

    private static final User OWNER = SIMPLE_USER_1;
    private static final User SUPER = SUPER_USER;

    private AdvertiserSettings advertiser;

    @Before
    public void setUp() {
        advertiser = createSimpleAdvertiser(OWNER);
        setGrantMultiplier(SUPER, advertiser.getAdvertiserId(), 2.0);
    }

    @Test
    public void failedToUpdateGrants() {
        for (int i = 0; i < 1000; i++) {
            List<Grant> grants;
            if (i % 2 == 0) {
                grants =
                        singletonList(new Grant().withUserLogin(READ_GUEST.toString()).withPermission(Permission.VIEW));
            } else {
                grants = emptyList();
            }
            V1ManagementAdvertiserAdvertiserIdPUTSchema response =
                    UserSteps.withUser(OWNER).onAdvertisersSteps()
                            .updateAdvertiser(advertiser.getAdvertiserId(), advertiser.withGrants(grants));
            //quota fail
            if (response != null && response.getCode() != null && response.getCode() == 429) {
                //fail too early
                if (i < 2) {
                    throw new AssumptionException("Квота закончилась слишком рано");
                }
                //noinspection unchecked
                TestSteps.assumeThat(ERROR_MESSAGE, response, expectError(QUOTA_EXCEEDED));
                return;
            }
        }
        //квота так и не закончилась. Кидаем ошибку
        throw new AssumptionException("Не удалось превысить квоту");
    }

    @After
    public void cleanUp() {
        UserSteps.withUser(OWNER).onAdvertisersSteps().deleteAdvertiserAndExpectSuccess(advertiser.getAdvertiserId());
        deleteGrantMultiplier(SUPER, advertiser.getAdvertiserId());
    }
}
