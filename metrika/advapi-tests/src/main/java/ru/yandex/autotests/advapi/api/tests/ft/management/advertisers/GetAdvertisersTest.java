package ru.yandex.autotests.advapi.api.tests.ft.management.advertisers;

import org.hamcrest.Matcher;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.advapi.data.users.User;
import ru.yandex.autotests.advapi.parameters.AdvertiserManagementParameters;
import ru.yandex.autotests.advapi.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static java.util.Arrays.asList;
import static org.hamcrest.Matchers.*;
import static ru.yandex.autotests.advapi.api.tests.ft.management.AdvApiFeatures.MANAGEMENT;
import static ru.yandex.autotests.advapi.data.users.Users.*;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;

@Features(MANAGEMENT)
@Title("Получение рекламодателей")
@RunWith(Parameterized.class)
public class GetAdvertisersTest {

    @Parameterized.Parameter()
    public User user;

    @Parameterized.Parameter(1)
    public AdvertiserManagementParameters parameters;

    @Parameterized.Parameter(2)
    public Matcher matcher;

    @Parameterized.Parameter(3)
    public String message;

    @Parameterized.Parameters(name = "{3}")
    public static Collection<Object[]> createParameters() {
        return asList(new Object[][]{
                {
                        SIMPLE_USER_1,
                        new AdvertiserManagementParameters(),
                        iterableWithSize(greaterThanOrEqualTo(2)),
                        SIMPLE_USER_1 + " имеет доступ к 2 рекламодателям"
                },
                {
                        SUPER_USER,
                        new AdvertiserManagementParameters().withUid(SIMPLE_USER_1.get(User.UID)),
                        iterableWithSize(greaterThanOrEqualTo(2)),
                        SUPER_USER + " имеет доступ к 2 рекламодателям"
                },
                {
                        SUPERVISOR,
                        new AdvertiserManagementParameters().withUid(SIMPLE_USER_1.get(User.UID)),
                        iterableWithSize(greaterThanOrEqualTo(2)),
                        SUPERVISOR + " имеет доступ к 2 рекламодателю"
                },
                {
                        SIMPLE_USER_1,
                        new AdvertiserManagementParameters().withLimit(0),
                        empty(),
                        "пустой список рекламодателей"
                },
                {
                        SIMPLE_USER_1,
                        new AdvertiserManagementParameters().withLimit(1),
                        iterableWithSize(greaterThanOrEqualTo(1)),
                        "список из 1 рекламодателя"
                },
                {
                        SIMPLE_USER_1,
                        new AdvertiserManagementParameters().withOffset(Integer.MAX_VALUE),
                        empty(),
                        "пустой список рекламодателей"
                },
                {
                        SIMPLE_USER_1,
                        new AdvertiserManagementParameters().withOffset(1),
                        iterableWithSize(greaterThanOrEqualTo(1)),
                        "список из 1 рекламодателя"
                }
        });
    }

    @Test
    public void getAdvertisers() {
        assertThat(message, UserSteps.withUser(user).onAdvertisersSteps().getAdvertisersAndExpectSuccess(parameters).getAdvertisers(), matcher);
    }
}
