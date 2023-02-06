package ru.yandex.autotests.advapi.api.tests.ft.management.advertisers;

import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.advapi.V1ManagementAdvertisersPOSTRequestSchema;
import ru.yandex.autotests.advapi.data.users.User;
import ru.yandex.autotests.advapi.steps.UserSteps;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.metrika.adv.api.management.advertiser.external.AdvertiserSettings;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static java.util.Arrays.asList;
import static ru.yandex.autotests.advapi.Errors.*;
import static ru.yandex.autotests.advapi.api.tests.ft.management.AdvApiFeatures.MANAGEMENT;
import static ru.yandex.autotests.advapi.api.tests.ft.management.ManagementTestUtils.getTooLongName;
import static ru.yandex.autotests.advapi.data.users.Users.SIMPLE_USER_1;

@Features(MANAGEMENT)
@Title("Создания рекламодателя (негативные)")
@RunWith(Parameterized.class)
public class CreateAdvertisersNegativeTest {

    private static final User OWNER = SIMPLE_USER_1;

    private V1ManagementAdvertisersPOSTRequestSchema body;

    @Parameterized.Parameter()
    public AdvertiserSettings advertiser;

    @Parameterized.Parameter(1)
    public IExpectedError error;

    @Parameterized.Parameter(2)
    public String title;

    @Parameterized.Parameters(name = "{2}")
    public static Collection<Object[]> createParameters() {
        return asList(new Object[][]{
                {
                        new AdvertiserSettings().withName(""),
                        SIZE_MUST_BE_BETWEEN,
                        "создание рекламодателя с пустым именем ведет к ошибке"
                },
                {
                        new AdvertiserSettings().withName(getTooLongName()),
                        SIZE_MUST_BE_BETWEEN,
                        "создание рекламодателя с имени размером больше 256 символов ведет к ошибке"
                },
                {
                        new AdvertiserSettings().withPostViewDays(0L),
                        MUST_BE_GREATER_OR_EQUAL,
                        "post-view не может быть 0"
                },
                {
                        new AdvertiserSettings().withPostViewDays(91L),
                        MUST_BE_LESS_OR_EQUAL,
                        "post-view не может превышать 90 дней"
                },
                {
                        new AdvertiserSettings().withPostClickDays(0L),
                        MUST_BE_GREATER_OR_EQUAL,
                        "post-click не может быть 0"
                },
                {
                        new AdvertiserSettings().withPostClickDays(31L),
                        MUST_BE_LESS_OR_EQUAL,
                        "post-click не может превышать 30 дней"
                }
        });
    }

    @Before
    public void setUp() {
        body = new V1ManagementAdvertisersPOSTRequestSchema().withAdvertiser(advertiser);
    }

    @Test
    public void failToCreateAdvertiser() {
        UserSteps.withUser(OWNER).onAdvertisersSteps().addAdvertisersAndExpectError(body, error);
    }
}
