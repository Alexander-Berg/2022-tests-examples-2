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
import static ru.yandex.autotests.advapi.Errors.*;
import static ru.yandex.autotests.advapi.api.tests.ft.management.AdvApiFeatures.MANAGEMENT;
import static ru.yandex.autotests.advapi.api.tests.ft.management.ManagementTestUtils.*;
import static ru.yandex.autotests.advapi.data.users.Users.*;

@Features(MANAGEMENT)
@Title("Изменение рекламодателя (негативные)")
@RunWith(Parameterized.class)
public class UpdateAdvertiserNegativeTest {

    private static final User OWNER = SIMPLE_USER_1;
    private static final User GUEST = SIMPLE_USER_A;

    private long advertiserId;

    @Parameterized.Parameter()
    public AdvertiserSettings orig;

    @Parameterized.Parameter(1)
    public User otherUser;

    @Parameterized.Parameter(2)
    public AdvertiserSettings update;

    @Parameterized.Parameter(3)
    public IExpectedError error;

    @Parameterized.Parameter(4)
    public String title;

    @Parameterized.Parameters(name = "{4}")
    public static Collection<Object[]> createParameters() {
        return asList(new Object[][]{
                {
                        getAdvertiserSettings(),
                        OWNER,
                        new AdvertiserSettings().withName(""),
                        SIZE_MUST_BE_BETWEEN,
                        "нельзя установить рекламодателю пустое имя"
                },
                {
                        getAdvertiserSettings(),
                        OWNER,
                        new AdvertiserSettings()
                                .withName(getTooLongName()),
                        SIZE_MUST_BE_BETWEEN,
                        "нельзя установить рекламодателю имя длиннее 256 символов"
                },
                {
                        getAdvertiserSettings(),
                        GUEST,
                        new AdvertiserSettings(),
                        ACCESS_DENIED,
                        "случайный пользователь не может изменять рекламодателя"
                },
                {
                        getAdvertiserSettings(),
                        SUPERVISOR,
                        new AdvertiserSettings(),
                        ACCESS_DENIED,
                        "суперсмотритель не может изменять рекламодателя"
                },
                {
                        getAdvertiserSettings(GUEST, Permission.VIEW),
                        GUEST,
                        new AdvertiserSettings(),
                        ACCESS_DENIED,
                        "случайный пользователь с разрешением на просмотр не может изменять рекламодателя"
                },
                {
                        getAdvertiserSettings(),
                        OWNER,
                        new AdvertiserSettings().withPostClickDays(0L),
                        MUST_BE_GREATER_OR_EQUAL,
                        "post-click должны быть больше 0"
                },
                {
                        getAdvertiserSettings(),
                        OWNER,
                        new AdvertiserSettings().withPostClickDays(31L),
                        MUST_BE_LESS_OR_EQUAL,
                        "post-click не могут превышать 30 дней"
                },
                {
                        getAdvertiserSettings(),
                        OWNER,
                        new AdvertiserSettings().withPostViewDays(0L),
                        MUST_BE_GREATER_OR_EQUAL,
                        "post-view должны быть больше 0"
                },
                {
                        getAdvertiserSettings(),
                        OWNER,
                        new AdvertiserSettings().withPostViewDays(91L),
                        MUST_BE_LESS_OR_EQUAL,
                        "post-view не могут превышать 90 дней"
                }
        });
    }

    @Before
    public void setUp() {
        advertiserId = createAdvertiser(OWNER, orig).getAdvertiserId();
    }

    @Test
    public void updateAdvertiser() {
        UserSteps.withUser(otherUser).onAdvertisersSteps().updateAdvertiserAndExpectError(advertiserId, update, error);
    }

    @After
    public void clean() {
        UserSteps.withUser(OWNER).onAdvertisersSteps().deleteAdvertiserAndExpectSuccess(advertiserId);
    }
}
