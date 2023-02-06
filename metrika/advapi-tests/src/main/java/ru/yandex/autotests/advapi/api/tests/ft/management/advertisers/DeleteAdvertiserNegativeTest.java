package ru.yandex.autotests.advapi.api.tests.ft.management.advertisers;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.advapi.data.users.User;
import ru.yandex.autotests.advapi.steps.UserSteps;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.metrika.adv.api.management.advertiser.external.AdvertiserSettings;
import ru.yandex.metrika.rbac.Permission;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static java.util.Arrays.asList;
import static ru.yandex.autotests.advapi.Errors.ACCESS_DENIED;
import static ru.yandex.autotests.advapi.api.tests.ft.management.AdvApiFeatures.MANAGEMENT;
import static ru.yandex.autotests.advapi.api.tests.ft.management.ManagementTestUtils.createAdvertiser;
import static ru.yandex.autotests.advapi.api.tests.ft.management.ManagementTestUtils.getAdvertiserSettings;
import static ru.yandex.autotests.advapi.data.users.Users.*;

@Features(MANAGEMENT)
@Title("Удаления рекламодателя (негативные)")
@RunWith(Parameterized.class)
public class DeleteAdvertiserNegativeTest {

    private static final User OWNER = SIMPLE_USER_1;
    private static final User GUEST = SIMPLE_USER_A;

    private long advertiserId;

    @Parameterized.Parameter()
    public AdvertiserSettings settings;

    @Parameterized.Parameter(1)
    public User user;

    @Parameterized.Parameter(2)
    public IExpectedError error;

    @Parameterized.Parameter(3)
    public String title;

    @Parameterized.Parameters(name = "{3}")
    public static Collection<Object[]> createParameters() {
        return asList(new Object[][]{
                {
                        getAdvertiserSettings(),
                        GUEST,
                        ACCESS_DENIED,
                        "пользователь не может удалить чужую кампанию"
                },
                {
                        getAdvertiserSettings(),
                        SUPERVISOR,
                        ACCESS_DENIED,
                        "суперсмотритель не может удалить чужую кампанию"
                },
                {
                        getAdvertiserSettings(GUEST, Permission.VIEW),
                        GUEST,
                        ACCESS_DENIED,
                        "пользователь с разрешением на просмотр не может удалить чужую кампанию"
                },
                {
                        getAdvertiserSettings(GUEST, Permission.EDIT),
                        GUEST,
                        ACCESS_DENIED,
                        "пользователь с разешением на редактирование не может удалить чужую кампанию"
                }
        });
    }

    @Before
    public void setUp() {
        advertiserId = createAdvertiser(OWNER, settings).getAdvertiserId();
    }

    @Test
    public void failToDeleteAdvertiser() {
        UserSteps.withUser(user).onAdvertisersSteps().deleteAdvertiserAndExpectError(advertiserId, error);
    }

    @After
    public void cleanUp() {
        UserSteps.withUser(OWNER).onAdvertisersSteps().deleteAdvertiserAndExpectSuccess(advertiserId);
    }
}
