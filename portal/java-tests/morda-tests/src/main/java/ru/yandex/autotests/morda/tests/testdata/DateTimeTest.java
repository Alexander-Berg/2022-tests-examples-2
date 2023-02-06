package ru.yandex.autotests.morda.tests.testdata;

import org.apache.log4j.Logger;
import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.aqua.annotations.project.Feature;
import ru.yandex.autotests.morda.api.MordaClient;
import ru.yandex.autotests.morda.rules.allure.AllureLoggingRule;
import ru.yandex.geobase.regions.Afghanistan;
import ru.yandex.geobase.regions.AntiguaAndBarbuda;
import ru.yandex.geobase.regions.Argentina;
import ru.yandex.geobase.regions.Australia;
import ru.yandex.geobase.regions.Belarus;
import ru.yandex.geobase.regions.Brazil;
import ru.yandex.geobase.regions.Canada;
import ru.yandex.geobase.regions.DominicanRepublic;
import ru.yandex.geobase.regions.GeobaseRegion;
import ru.yandex.geobase.regions.Germany;
import ru.yandex.geobase.regions.India;
import ru.yandex.geobase.regions.Iran;
import ru.yandex.geobase.regions.Japan;
import ru.yandex.geobase.regions.Kazakhstan;
import ru.yandex.geobase.regions.Nepal;
import ru.yandex.geobase.regions.Portugal;
import ru.yandex.geobase.regions.Russia;
import ru.yandex.geobase.regions.Samoa;
import ru.yandex.geobase.regions.Switzerland;
import ru.yandex.geobase.regions.Ukraine;
import ru.yandex.geobase.regions.UnitedKingdom;
import ru.yandex.geobase.regions.UnitedStates;
import ru.yandex.geobase.regions.Venezuela;

import java.io.IOException;
import java.text.ParseException;
import java.time.Duration;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.Arrays;
import java.util.Collection;

import static javax.ws.rs.core.UriBuilder.fromUri;
import static org.hamcrest.CoreMatchers.equalTo;
import static org.hamcrest.MatcherAssert.assertThat;
import static ru.yandex.autotests.morda.utils.cookie.MordaCookieUtils.YANDEX_GID;

/**
 * User: asamar
 * Date: 02.11.16
 */

@Aqua.Test(title = "Время на RC и в продакшене")
@Feature("DateTime")
@RunWith(Parameterized.class)
public class DateTimeTest {
    @Parameterized.Parameters(name = "{0}")
    public static Collection<GeobaseRegion> data() throws Exception {
        return Arrays.asList(
                UnitedStates.HONOLULU, UnitedStates.ANCHORAGE, UnitedStates.LOS_ANGELES,
                UnitedStates.DENVER,  UnitedStates.DETROIT, UnitedStates.SAN_JOSE,
                UnitedStates.NEW_YORK, Canada.TORONTO, Canada.CALGARY, Canada.VANCOUVER, Samoa.PAGO_PAGO, Venezuela.CARACAS,
                DominicanRepublic.SANTO_DOMINGO, AntiguaAndBarbuda.ST_JOHN_S, Argentina.BUENOS_AIRES, Brazil.RIO_DE_JANEIRO,
                Portugal.PONTA_DELGADA, UnitedKingdom.LONDON, Portugal.LISBON, Germany.MUNICH, Switzerland.BERN,
                Ukraine.KYIV, Belarus.MINSK, Iran.TEHRAN, Russia.KALININGRAD, Russia.MOSCOW, Russia.SAINT_PETERSBURG,
                Afghanistan.KABUL, Kazakhstan.AKTOBE, India.MUMBAI, Nepal.KATHMANDU, Russia.YEKATERINBURG, Kazakhstan.ASTANA,
                Russia.OMSK, Russia.NOVOSIBIRSK, Russia.KRASNOYARSK, Russia.IRKUTSK, Japan.TOKYO, Australia.ADELAIDE,
                Russia.YAKUTSK, Russia.NAHODKA, Russia.MAGADAN
        );

    }

    @Rule
    public AllureLoggingRule rule = new AllureLoggingRule();
    private static final DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");
    private static Logger LOGGER = Logger.getLogger(DateTimeTest.class);
    private static final int MAX_DIFFERENCE = 5;

    private GeobaseRegion region;
    private Duration duration;

    public DateTimeTest(GeobaseRegion region) {
        this.region = region;
    }

    @Before
    public void init() {
        LocalDateTime rcTime = getRcDateTime(region);
        LocalDateTime prodTime = getProdDateTime(region);

        this.duration = Duration.between(rcTime, prodTime).abs();
    }

    @Test
    public void compareTime() throws IOException, ParseException {
        int timeDifference = duration.compareTo(Duration.ofMinutes(MAX_DIFFERENCE));

        assertThat("Разница времени на RC от продакшена в " + region + " больше 5 минут", timeDifference, equalTo(-1));
    }

    private LocalDateTime getRcDateTime(GeobaseRegion region) {
        return getTime("www-rc", region);
    }

    private LocalDateTime getProdDateTime(GeobaseRegion region) {
        return getTime("www", region);
    }

    private LocalDateTime getTime(String env, GeobaseRegion region) {
        String urlPattern = "https://%s.yandex%s";
        String url = String.format(urlPattern, env, region.getKubrDomain());

        String dateTime = new MordaClient()
                .cleanvars(fromUri(url).build())
                .cookie(YANDEX_GID, String.valueOf(region.getRegionId()))
                .read()
                .getHiddenTime();

        LOGGER.info(region + " " + dateTime + " on " + fromUri(url).build().getHost());
        return LocalDateTime.parse(dateTime, formatter);
    }
}

