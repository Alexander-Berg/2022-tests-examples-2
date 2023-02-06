package ru.yandex.autotests.advapi.api.tests.ft.management.campaigns;

import org.hamcrest.Matcher;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.advapi.data.users.User;
import ru.yandex.autotests.advapi.parameters.CampaignManagementParameters;
import ru.yandex.autotests.advapi.parameters.CampaignStatus;
import ru.yandex.autotests.advapi.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static java.util.Arrays.asList;
import static org.hamcrest.Matchers.*;
import static ru.yandex.autotests.advapi.api.tests.ft.management.AdvApiFeatures.MANAGEMENT;
import static ru.yandex.autotests.advapi.data.users.Users.*;
import static ru.yandex.autotests.advapi.parameters.CampaignsSort.days_left;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;

@Features(MANAGEMENT)
@Title("Получение списка кампаний")
@RunWith(Parameterized.class)
public class GetCampaignsTest {

    @Parameterized.Parameter()
    public User user;

    @Parameterized.Parameter(1)
    public Matcher matcher;

    @Parameterized.Parameter(2)
    public CampaignManagementParameters parameters;

    @Parameterized.Parameter(3)
    public String message;


    @Parameterized.Parameters(name = "{3}")
    public static Collection<Object[]> createParameters() {
        return asList(new Object[][]{
                {
                        SIMPLE_USER_1,
                        hasItems(
                                hasProperty("campaignId", equalTo(256L)),
                                hasProperty("campaignId", equalTo(259L)),
                                hasProperty("campaignId", equalTo(262L)),
                                hasProperty("campaignId", equalTo(265L)),
                                hasProperty("campaignId", equalTo(280L))
                        ),
                        new CampaignManagementParameters().withAdvertiserId(196),
                        "возвращается 5 кампаний отсортиованные по имени"
                },
                {
                        SIMPLE_USER_1,
                        iterableWithSize(1),
                        new CampaignManagementParameters().withLimit(1),
                        "кампания 256 присутствует"
                },
                {
                        SIMPLE_USER_1,
                        hasItem(hasProperty("campaignId", equalTo(280L))),
                        new CampaignManagementParameters().withAdvertiserId(196).withReversed(true).withLimit(1),
                        "кампания 280 присутствует"
                },
                {
                        SIMPLE_USER_1,
                        hasItem(hasProperty("campaignId", equalTo(265L))),
                        new CampaignManagementParameters().withAdvertiserId(196).withReversed(true).withLimit(1).withOffset(1),
                        "кампания 265 присутствует"
                },
                {
                        SIMPLE_USER_1,
                        hasItem(hasProperty("campaignId", equalTo(265L))),
                        new CampaignManagementParameters().withAdvertiserId(196).withSort(days_left).withLimit(1),
                        "кампания 265 присутствует"
                },
                {
                        SIMPLE_USER_1,
                        iterableWithSize(greaterThanOrEqualTo(1)),
                        new CampaignManagementParameters().withAdvertiserId(196).withStatus(CampaignStatus.archived),
                        "заархивированна 1 компания"
                },
                {
                        SIMPLE_USER_1,
                        iterableWithSize(greaterThanOrEqualTo(2)),
                        new CampaignManagementParameters().withLimit(2),
                        "длина списка кампаний равна 2"
                },
                {
                        SIMPLE_USER_1,
                        empty(),
                        new CampaignManagementParameters().withLimit(0),
                        "список кампаний пуст"
                },
                {
                        SIMPLE_USER_1,
                        empty(),
                        new CampaignManagementParameters().withOffset(Integer.MAX_VALUE),
                        "список кампаний пуст"
                },
                {
                        SIMPLE_USER_1,
                        iterableWithSize(greaterThanOrEqualTo(3)),
                        new CampaignManagementParameters().withAdvertiserId(196).withOffset(2),
                        "возвращается 4 кампании"
                },
                {
                        SIMPLE_USER_1,
                        iterableWithSize(greaterThanOrEqualTo(4)),
                        new CampaignManagementParameters().withAdvertiserId(196).withFilter("cmp"),
                        "кампания с подстрокой 'cmp' в имени присутствует"
                },
                {
                        SIMPLE_USER_1,
                        empty(),
                        new CampaignManagementParameters().withFilter("not existing campaign"),
                        "кампания с именем 'not existing campaign' отсутствует"
                },
                {
                        SIMPLE_USER_1,
                        hasItem(hasProperty("campaignId", equalTo(265L))),
                        new CampaignManagementParameters().withFrom("2019-02-01").withTo("2019-03-01"),
                        "кампания, проходящяя между 2019-02-01 и 2019-03-01 присутствует (265)"
                },
                {
                        SIMPLE_USER_A,
                        hasItems(
                                hasProperty("campaignId", equalTo(283L)),
                                hasProperty("campaignId", equalTo(268L)),
                                hasProperty("campaignId", equalTo(271L))
                        ),
                        new CampaignManagementParameters(),
                        SIMPLE_USER_A + " имеет доступ к 3 кампаниям"
                },
                {
                        SUPER_USER,
                        iterableWithSize(greaterThanOrEqualTo(6)),
                        new CampaignManagementParameters().withUid(SIMPLE_USER_1.get(User.UID)),
                        SUPER_USER + " имеет доступ к 6 кампаниям"
                },
                {
                        SUPER_USER,
                        iterableWithSize(greaterThanOrEqualTo(5)),
                        new CampaignManagementParameters().withAdvertiserId(196L),
                        SUPER_USER + " имеет доступ к 5 кампаниям рекламодателя 196"
                },
                {
                        SUPERVISOR,
                        iterableWithSize(greaterThanOrEqualTo(6)),
                        new CampaignManagementParameters().withUid(SIMPLE_USER_1.get(User.UID)),
                        SUPERVISOR + " имеет доступ к 6 кампаниям"
                },
                {
                        SUPERVISOR,
                        iterableWithSize(greaterThanOrEqualTo(5)),
                        new CampaignManagementParameters().withAdvertiserId(196L),
                        SUPERVISOR + " имеет доступ к 5 кампаниям рекламодателя 196"
                },
        });
    }

    @Test
    public void getCampaigns() {
        assertThat(message, UserSteps.withUser(user).onCampaignsSteps().getCampaignsAndExpectSuccess(parameters).getCampaigns(), matcher);
    }
}
