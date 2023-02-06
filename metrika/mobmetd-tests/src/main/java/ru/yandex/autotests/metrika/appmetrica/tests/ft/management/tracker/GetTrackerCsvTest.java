package ru.yandex.autotests.metrika.appmetrica.tests.ft.management.tracker;

import com.google.common.collect.ImmutableList;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.appmetrica.core.AppMetricaCsvResponse;
import ru.yandex.autotests.metrika.appmetrica.info.csv.CsvCampaign;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Arrays;
import java.util.Collection;
import java.util.List;
import java.util.stream.Collectors;

import static org.apache.commons.lang3.ArrayUtils.toArray;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.appmetrica.data.Users.READ_USER;
import static ru.yandex.autotests.metrika.appmetrica.matchers.ResponseMatchers.equivalentTo;

/**
 * @author dancingelf
 */
@Features(Requirements.Feature.Management.TRACKER)
@Stories({
        Requirements.Story.Tracker.CSV,
})
@RunWith(Parameterized.class)
@Title("Получение csv с описанием трекеров")
public class GetTrackerCsvTest {

    @Parameterized.Parameter
    public String locale;

    @Parameterized.Parameter(1)
    public List<String> headers;

    @Parameterized.Parameters(name = "Локаль: {0}; Заголовок: {1}")
    public static Collection<Object[]> createParameters() {
        return ImmutableList.of(
                param("ru", Arrays.asList("Идентификатор трекера", "Название трекера", "Идентификатор приложения", "Время создания")),
                param("en", Arrays.asList("Tracker ID", "Tracker name", "Application ID", "Creation time"))
        );
    }

    private UserSteps userSteps;
    private AppMetricaCsvResponse<CsvCampaign> actualCsv;

    @Before
    public void setup() {
        userSteps = UserSteps.onTesting(READ_USER);
        actualCsv = userSteps.onTrackerSteps().getTrackerCsv(locale);
    }

    @Test
    public void testHeaders() {
        assertThat("заголовок корректен", actualCsv.getHeaders(), equivalentTo(headers));
    }

    @Test
    public void testCsvContent() {
        List<CsvCampaign> actualCampaigns = actualCsv.getContent();
        List<CsvCampaign> expectedCampaigns = userSteps.onTrackerSteps().getTrackerList().stream()
                .map(jsonCampaign -> new CsvCampaign(
                        jsonCampaign.getTrackingId(),
                        jsonCampaign.getName(),
                        jsonCampaign.getApiKey(),
                        jsonCampaign.getCreateTime()
                ))
                .collect(Collectors.toList());
        assertThat("данные csv и json запросов совпадают", actualCampaigns, equivalentTo(expectedCampaigns));
    }

    private static Object[] param(String locale, List<String> headers) {
        return toArray(locale, headers);
    }
}
