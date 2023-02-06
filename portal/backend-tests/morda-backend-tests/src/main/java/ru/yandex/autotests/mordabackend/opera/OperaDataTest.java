package ru.yandex.autotests.mordabackend.opera;

import com.fasterxml.jackson.databind.JsonNode;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mordabackend.MordaClient;
import ru.yandex.autotests.mordabackend.Properties;
import ru.yandex.autotests.utils.morda.BaseProperties;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.autotests.utils.morda.url.Domain;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import java.util.Arrays;
import java.util.Collection;
import java.util.List;

import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.greaterThanOrEqualTo;
import static org.junit.Assert.assertTrue;
import static ru.yandex.autotests.utils.morda.ParametrizationConverter.convert;
import static ru.yandex.autotests.utils.morda.region.Region.ASTANA;
import static ru.yandex.autotests.utils.morda.region.Region.KIEV;
import static ru.yandex.autotests.utils.morda.region.Region.MINSK;
import static ru.yandex.autotests.utils.morda.region.Region.MOSCOW;
import static ru.yandex.autotests.utils.morda.region.Region.SPB;

/**
 * @author Ivan Nikolaev <ivannik@yandex-team.ru>
 */
@Aqua.Test(title = "Opera Data Samsung Combined")
@Features("Opera")
@Stories("Opera Data Samsung Combined")
@RunWith(Parameterized.class)
public class OperaDataTest {
    private static final Properties CONFIG = new Properties();
    private static final List<String> NULLABLE_FIELDS = Arrays.asList("IsHoliday");
    private static final List<String> EXPECTED_FIELDS = Arrays.asList(
            "IsHoliday", "Topnews", "Notifications", "OPVer", "SearchUrl", "HiddenTime", "BigLongMonth",
            "SocialProvidersList", "BigCityName", "OurNotifications", "HideThisWidget",
            "Afisha", "BigLongWday", "Traffic", "SocialProviders", "AuthInfo", "BigShortWday", "Weather",
            "BigShortMonthCapital", "SmartExample", "BigCityNamePre", "Search", "yu", "NcRnd",
            "BigCityNameLocative", "Stocks", "Mail", "BigShortMonth", "Generic", "BigCityHeadLengthV2", "TV",
            "BigWday", "BigDay", "BigMonth");
    private final Region region;
    private final MordaClient mordaClient;
    public OperaDataTest(Region region) {
        this.region = region;
        this.mordaClient = new MordaClient(
                CONFIG.getProtocol(),
                new BaseProperties.MordaEnv(CONFIG.getMordaEnv().getEnv().replace("www-", "op-")),
                Domain.RU);
    }

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> data() {
        return convert(Arrays.asList(MOSCOW, SPB, KIEV, MINSK, ASTANA));
    }

    @Test
    public void operaDataSamsungCombined() {
        JsonNode operaDataResponse = mordaClient.operaDataActions().getDataSamsungCombined(region.getRegionId());
        for (String fieldName : EXPECTED_FIELDS) {
            if (NULLABLE_FIELDS.contains(fieldName)) {
                assertTrue("Field " + fieldName + " not exists", operaDataResponse.has(fieldName));
            } else {
                assertTrue("Field " + fieldName + " not exists", operaDataResponse.hasNonNull(fieldName));
            }
        }
        assertThat("Wrong number of fields", operaDataResponse.size(), greaterThanOrEqualTo(10));
    }
}
