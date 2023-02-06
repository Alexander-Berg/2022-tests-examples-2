package ru.yandex.autotests.metrika.appmetrica.tests.ft.management.partner;

import com.google.common.collect.ImmutableList;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.appmetrica.core.AppMetricaCsvResponse;
import ru.yandex.autotests.metrika.appmetrica.info.csv.CsvPartner;
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
@Features(Requirements.Feature.Management.PARTNERS)
@Stories({
        Requirements.Story.Partner.CSV,
})
@RunWith(Parameterized.class)
@Title("Получение csv с описанием партнеров")
public class GetPartnerCsvTest {

    private UserSteps userSteps;

    @Parameterized.Parameter
    public String locale;

    @Parameterized.Parameter(1)
    public List<String> headers;

    @Parameterized.Parameters(name = "Локаль: {0}; Заголовки: {1}")
    public static Collection<Object[]> createParameters() {
        return ImmutableList.of(
                param("ru", Arrays.asList("Идентификатор партнёра", "Название партнёра", "Веб-сайт")),
                param("en", Arrays.asList("Partner ID", "Partner name", "Website"))
        );
    }

    private AppMetricaCsvResponse<CsvPartner> actualCsvResponse;

    @Before
    public void setup() {
        userSteps = UserSteps.onTesting(READ_USER);
        actualCsvResponse = userSteps.onPartnerSteps().getPartnerCsv(locale);
    }

    @Test
    public void testHeaders() {
        assertThat("заголовок корректен", actualCsvResponse.getHeaders(), equivalentTo(headers));
    }

    @Test
    public void testContent() {
        List<CsvPartner> actualPartners = actualCsvResponse.getContent();
        List<CsvPartner> expectedPartners = userSteps.onPartnerSteps().getPartnersList().stream()
                .map(jsonPartner -> new CsvPartner(
                        jsonPartner.getId(),
                        jsonPartner.getName(),
                        // в бд сайт почему то может быть пустой строкой. В csv мы не можем заметить
                        // разлицу между null и пустой строкой.
                        jsonPartner.getWebsiteUrl() == null ? "" : jsonPartner.getWebsiteUrl()))
                .collect(Collectors.toList());
        assertThat("данные csv и json запросов совпадают", actualPartners, equivalentTo(expectedPartners));
    }

    private static Object[] param(String locale, List<String> headers) {
        return toArray(locale, headers);
    }
}
