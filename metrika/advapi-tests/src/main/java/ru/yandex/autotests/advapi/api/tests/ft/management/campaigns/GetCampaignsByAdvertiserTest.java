package ru.yandex.autotests.advapi.api.tests.ft.management.campaigns;

import org.hamcrest.Matcher;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.advapi.data.users.User;
import ru.yandex.autotests.advapi.parameters.CampaignManagementParameters;
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
@Title("Получение кампании по рекламодателю")
@RunWith(Parameterized.class)
public class GetCampaignsByAdvertiserTest {

    private static final User OWNER = SIMPLE_USER_1;
    private static final int ADVERTISER_ID = 196;

    @Parameterized.Parameter()
    public User user;

    @Parameterized.Parameter(1)
    public CampaignManagementParameters parameters;

    @Parameterized.Parameter(2)
    public Matcher matcher;

    @Parameterized.Parameter(3)
    public String message;

    @Parameterized.Parameters(name = "{3}")
    public static Collection<Object[]> createParameters() {
        return asList(new Object[][]{
                {
                        OWNER,
                        new CampaignManagementParameters(),
                        contains(asList(
                                hasProperty("campaignId", equalTo(256L)),
                                hasProperty("campaignId", equalTo(259L)),
                                hasProperty("campaignId", equalTo(262L)),
                                hasProperty("campaignId", equalTo(265L)),
                                hasProperty("campaignId", equalTo(280L))
                        )),
                        "возвращается 5 кампаний отсортиованные по имени"
                },
                {
                        OWNER,
                        new CampaignManagementParameters().withLimit(1),
                        contains(hasProperty("campaignId", equalTo(256L))),
                        "кампания 256 присутствует"
                },
                {
                        OWNER,
                        new CampaignManagementParameters().withLimit(2),
                        iterableWithSize(greaterThanOrEqualTo(2)),
                        "длина списка кампаний равна 2"
                },
                {
                        OWNER,
                        new CampaignManagementParameters().withLimit(0),
                        empty(),
                        "список кампаний пуст"
                },
                {
                        OWNER,
                        new CampaignManagementParameters().withOffset(Integer.MAX_VALUE),
                        empty(),
                        "список кампаний пуст"
                },
                {
                        OWNER,
                        new CampaignManagementParameters().withOffset(2),
                        iterableWithSize(greaterThanOrEqualTo(3)),
                        "возвращается 3 кампании"
                },
                {
                        READ_GUEST,
                        new CampaignManagementParameters(),
                        iterableWithSize(greaterThanOrEqualTo(5)),
                        "пользователь с правами на чтение может просматривать кампании рекламодателя 196"
                },
                {
                        WRITE_GUEST,
                        new CampaignManagementParameters(),
                        iterableWithSize(greaterThanOrEqualTo(5)),
                        "пользователь с правами на редактирование может просматривать кампании рекламодателя 196"
                },
                {
                        SUPER_USER,
                        new CampaignManagementParameters(),
                        iterableWithSize(greaterThanOrEqualTo(5)),
                        "суперпользователь может просматривать кампании рекламодателя 196"
                },
                {
                        SUPERVISOR,
                        new CampaignManagementParameters(),
                        iterableWithSize(greaterThanOrEqualTo(5)),
                        "суперсмотритель может просматривать кампании рекламодателя 196"
                }
        });
    }

    @Test
    public void getCampaignsByAdvertiser() {
        assertThat(message, UserSteps.withUser(user).onCampaignsSteps().getCampaignsByAdvertiserAndExpectSuccess(ADVERTISER_ID, parameters).getCampaigns(), matcher);
    }
}
