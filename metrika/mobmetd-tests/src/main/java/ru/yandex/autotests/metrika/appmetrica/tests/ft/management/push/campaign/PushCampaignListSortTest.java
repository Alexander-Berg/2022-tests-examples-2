package ru.yandex.autotests.metrika.appmetrica.tests.ft.management.push.campaign;

import com.google.common.collect.Ordering;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.junit.runners.Parameterized.Parameter;
import org.junit.runners.Parameterized.Parameters;
import ru.yandex.autotests.metrika.appmetrica.data.Application;
import ru.yandex.autotests.metrika.appmetrica.data.Users;
import ru.yandex.autotests.metrika.appmetrica.parameters.PushCampaignsListParameters;
import ru.yandex.autotests.metrika.appmetrica.parameters.push.campaign.PushCampaignListSortField;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.autotests.metrika.commons.junitparams.combinatorial.CombinatorialBuilder;
import ru.yandex.metrika.mobmet.push.common.campaigns.adapters.PushCampaignBriefAdapter;
import ru.yandex.metrika.mobmet.push.common.campaigns.adapters.PushCampaignsAdapter;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;
import java.util.Comparator;
import java.util.List;

import static org.apache.commons.lang3.StringUtils.containsIgnoreCase;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.*;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assumeThat;
import static ru.yandex.autotests.metrika.appmetrica.data.Applications.PUSH_SAMPLE;
import static ru.yandex.autotests.metrika.appmetrica.matchers.ResponseMatchers.equivalentTo;

/**
 * Загрузим все пуш-кампании PUSH_SAMPLE и проверим, что они отсортированы.
 * Этот тест полезен, поскольку в апи логика составления списка пуш-кампаний сейчас мудрёная:
 * у нас два типа пуш-кампаний, загружаемых из разных таблиц.
 */
@Features(Requirements.Feature.Management.PUSH_CAMPAIGN)
@Stories({
        Requirements.Story.PushCampaign.LIST
})
@Title("Сортировка списка Push-кампаний")
@RunWith(Parameterized.class)
public class PushCampaignListSortTest {

    private static final UserSteps user = UserSteps.onTesting(Users.SUPER_LIMITED);

    private static final int BEGIN_OFFSET = 0;

    @Parameter
    public PushCampaignListSortField sortField;

    @Parameter(1)
    public String sortOrder;

    /**
     * В зависимости от этого параметра сортировка может идти в разных ветках
     */
    @Parameter(2)
    public boolean includePushApi;

    @Parameters(name = "sortField: {0}, sortOrder: {1}, includePushApi: {2}")
    public static Collection<Object[]> createParameters() {
        return CombinatorialBuilder.builder()
                .values(PushCampaignListSortField.values())
                .values("asc", "desc")
                .values(true, false)
                .build();
    }

    @Test
    public void checkAllOrdered() {
        // Настраиваем параметры так, чтобы загрузились все пуш-кампании PUSH_SAMPLE
        List<PushCampaignBriefAdapter> campaigns = user.onPushCampaignSteps()
                .getCampaignList(buildRequest(2000, BEGIN_OFFSET))
                .getCampaigns();
        assertThat("Список пуш-кампаний отсортировался", Ordering.from(buildComparator()).isOrdered(campaigns));
    }

    @Test
    public void checkLimited() {
        int limit = 100;
        PushCampaignsAdapter campaigns = user.onPushCampaignSteps()
                .getCampaignList(buildRequest(limit, BEGIN_OFFSET));
        assumeThat("Limit правильный", campaigns.getCampaigns(), hasSize(limit));
        assumeThat("Totals корректный", campaigns.getTotals(), greaterThan((long) limit));
        assertThat("Список пуш-кампаний отсортировался", Ordering.from(buildComparator()).isOrdered(campaigns.getCampaigns()));
    }

    @Test
    public void checkOffset() {
        int limit = 100;
        List<PushCampaignBriefAdapter> campaigns1 = user.onPushCampaignSteps()
                .getCampaignList(buildRequest(limit, BEGIN_OFFSET))
                .getCampaigns();
        List<PushCampaignBriefAdapter> campaigns2 = user.onPushCampaignSteps()
                .getCampaignList(buildRequest(limit, limit))
                .getCampaigns();

        assumeThat("Limit правильный", campaigns1, hasSize(limit));
        assumeThat("Limit правильный", campaigns2, hasSize(limit));

        // учитывая что разные тесты могут выполняться параллельно и сортировка может быть не только по дате создания,
        // то непонятно как проверить лучше
        assertThat("Offset на что-то влияет", campaigns1, not(equivalentTo(campaigns2)));
    }

    @Test
    public void checkMasked() {
        int limit = 500;
        String mask = "Test";

        PushCampaignsAdapter masked = user.onPushCampaignSteps()
                .getCampaignList(buildRequest(limit, BEGIN_OFFSET).withMask("Test"));

        PushCampaignsAdapter notMasked = user.onPushCampaignSteps()
                .getCampaignList(buildRequest(limit, BEGIN_OFFSET));

        int correctionForParallelTests = 10;
        assumeThat("Totals меньше", masked.getTotals(), lessThan(notMasked.getTotals() - correctionForParallelTests));
        assertThat("Список пуш-кампаний отсортировался", Ordering.from(buildComparator()).isOrdered(masked.getCampaigns()));
        boolean allMasked = true;
        for (PushCampaignBriefAdapter c : masked.getCampaigns()) {
            if (!containsIgnoreCase(c.getName(), mask) && !containsIgnoreCase(c.getOwnerLogin(), mask)) {
                allMasked = false;
                break;
            }
        }
        assertThat("Список пуш-кампаний отфильтрован", allMasked);
    }

    private Comparator<PushCampaignBriefAdapter> buildComparator() {
        if (sortOrder.equals("asc")) {
            return sortField.getComparator();
        } else {
            return sortField.getComparator().reversed();
        }
    }

    private PushCampaignsListParameters buildRequest(int limit, int offset) {
        return new PushCampaignsListParameters()
                .withAppId(PUSH_SAMPLE.get(Application.ID))
                .withOffset(offset)
                .withLimit(limit)
                .withIncludePushApi(includePushApi)
                .withSort(sortField.name())
                .withSortOrder(sortOrder);
    }
}
