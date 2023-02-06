package ru.yandex.autotests.metrika.appmetrica.tests.ft.management.push.campaign;

import com.google.common.collect.ImmutableList;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.junit.runners.Parameterized.Parameter;
import org.junit.runners.Parameterized.Parameters;
import ru.yandex.autotests.metrika.appmetrica.data.Application;
import ru.yandex.autotests.metrika.appmetrica.data.Applications;
import ru.yandex.autotests.metrika.appmetrica.data.Users;
import ru.yandex.autotests.metrika.appmetrica.parameters.PushCampaignsListParameters;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.metrika.mobmet.push.common.campaigns.adapters.PushCampaignBriefAdapter;
import ru.yandex.metrika.mobmet.push.common.campaigns.model.PushCampaignBriefInnerPushCampaignType;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;
import java.util.List;
import java.util.stream.Collectors;

import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.CoreMatchers.hasItem;
import static org.hamcrest.CoreMatchers.equalTo;
import static org.hamcrest.Matchers.empty;
import static org.hamcrest.Matchers.not;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assumeThat;

@Features(Requirements.Feature.Management.PUSH_CAMPAIGN)
@Stories({
        Requirements.Story.PushCampaign.LIST
})
@Title("Список пуш-кампаний, включающий Push API рассылки")
@RunWith(Parameterized.class)
public class PushCampaignListTest {
    private static final UserSteps user = UserSteps.onTesting(Users.SUPER_LIMITED);

    @Parameter
    public long appId;

    @Parameter(1)
    public int offset;

    @Parameter(2)
    public int limit;

    @Parameter(3)
    public String sort;

    @Parameter(4)
    public String sortOrder;

    @Parameters(name = "appId: {0}, offset: {1}, limit: {2}, sort: {3}. order: {4}")
    public static Collection<Object[]> createParameters() {
        // Задаём параметры так, чтобы получить список пуш-кампаний, включающий Push API при поднятом флажке
        // includePushApi и не включающий Push API при опущенном флажке includePushApi
        return ImmutableList.of(
                params(Applications.PUSH_SAMPLE.get(Application.ID), 11 * 25, 25, "date", "asc"));
    }

    @Test
    public void checkPushApiCampaignInList() {
        List<PushCampaignBriefInnerPushCampaignType> campaignTypes = loadPushCampaignTypes(true);

        assumeThat("Список пуш-кампаний не пустой", campaignTypes, not(empty()));

        assertThat("Список пуш-кампаний содержит хотя бы одну Push API рассылку",
                campaignTypes,
                hasItem(equalTo(PushCampaignBriefInnerPushCampaignType.PUSH_API_CAMPAIGN)));
    }

    @Test
    public void checkPushApiCampaignNotInList() {
        List<PushCampaignBriefInnerPushCampaignType> campaignTypes = loadPushCampaignTypes(false);

        assumeThat("Список пуш-кампаний не пустой", campaignTypes, not(empty()));

        assertThat("Список пуш-кампаний не содержит Push API рассылок",
                campaignTypes,
                not(hasItem(equalTo(PushCampaignBriefInnerPushCampaignType.PUSH_API_CAMPAIGN))));
    }

    private List<PushCampaignBriefInnerPushCampaignType> loadPushCampaignTypes(boolean includePushApi) {
        // Запрашиваем список пуш-кампаний для указанного target uid-а, потому что SUPER_LIMITED так может.
        // Иначе нужно было бы выдать грант на приложение, а для приложений yastorepublisher это делается только через IDM.
        long appOwnerUid = user.onApplicationSteps().getApplication(appId).getUid();
        return user.onPushCampaignSteps().getCampaignList(
                new PushCampaignsListParameters()
                        .withUid(appOwnerUid)
                        .withAppId(appId)
                        .withOffset(offset)
                        .withLimit(limit)
                        .withIncludePushApi(includePushApi)
                        .withSort(sort)
                        .withSortOrder(sortOrder))
                .getCampaigns()
                .stream()
                .map(PushCampaignBriefAdapter::getCampaignType)
                .collect(Collectors.toList());
    }

    private static Object[] params(long appId, int offset, int limit, String sort, String sortOrder) {
        return new Object[]{appId, offset, limit, sort, sortOrder};
    }
}
