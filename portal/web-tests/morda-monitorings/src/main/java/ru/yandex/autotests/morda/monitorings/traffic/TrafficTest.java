package ru.yandex.autotests.morda.monitorings.traffic;

import org.apache.commons.httpclient.util.HttpURLConnection;
import org.joda.time.LocalDateTime;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.morda.monitorings.MonitoringProperties;
import ru.yandex.autotests.morda.monitorings.rules.MordaMonitoringsRule;
import ru.yandex.autotests.mordabackend.MordaClient;
import ru.yandex.autotests.mordabackend.beans.cleanvars.Cleanvars;
import ru.yandex.autotests.mordabackend.beans.traffic.Future;
import ru.yandex.autotests.mordabackend.beans.traffic.Informer;
import ru.yandex.autotests.mordabackend.beans.traffic.Traffic;
import ru.yandex.autotests.mordabackend.cookie.Cookie;
import ru.yandex.autotests.mordabackend.cookie.CookieName;
import ru.yandex.autotests.mordabackend.headers.CookieHeader;
import ru.yandex.autotests.mordabackend.utils.TimeUtils;
import ru.yandex.autotests.utils.morda.ParametrizationConverter;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.qatools.allure.annotations.Features;

import javax.ws.rs.client.Client;
import java.io.IOException;
import java.util.Arrays;
import java.util.Collection;
import java.util.Collections;
import java.util.List;

import static ch.lambdaj.Lambda.extract;
import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.on;
import static org.hamcrest.Matchers.allOf;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.greaterThan;
import static org.hamcrest.Matchers.greaterThanOrEqualTo;
import static org.hamcrest.Matchers.hasSize;
import static org.hamcrest.Matchers.isEmptyOrNullString;
import static org.hamcrest.Matchers.lessThanOrEqualTo;
import static org.hamcrest.Matchers.not;
import static org.hamcrest.Matchers.notNullValue;
import static org.hamcrest.Matchers.nullValue;
import static org.junit.Assume.assumeFalse;
import static org.junit.Assume.assumeThat;
import static org.junit.Assume.assumeTrue;
import static ru.yandex.autotests.mordabackend.traffic.TrafficUtils.isFutureEnabled;
import static ru.yandex.autotests.mordabackend.traffic.TrafficUtils.skipDirection;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.shouldHaveParameter;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.shouldHaveResponseCode;
import static ru.yandex.autotests.utils.morda.region.Region.CHELYABINSK;
import static ru.yandex.autotests.utils.morda.region.Region.EKATERINBURG;
import static ru.yandex.autotests.utils.morda.region.Region.KAZAN;
import static ru.yandex.autotests.utils.morda.region.Region.KIEV;
import static ru.yandex.autotests.utils.morda.region.Region.MOSCOW;
import static ru.yandex.autotests.utils.morda.region.Region.NIZHNIY_NOVGOROD;
import static ru.yandex.autotests.utils.morda.region.Region.NOVOSIBIRSK;
import static ru.yandex.autotests.utils.morda.region.Region.PERM;
import static ru.yandex.autotests.utils.morda.region.Region.ROSTOV_NA_DONU;
import static ru.yandex.autotests.utils.morda.region.Region.SAMARA;
import static ru.yandex.autotests.utils.morda.region.Region.SANKT_PETERBURG;
import static ru.yandex.autotests.utils.morda.region.Region.VOLGOGRAD;

@Aqua.Test(title = "Пробки")
@Features("Пробки")
@RunWith(Parameterized.class)
public class TrafficTest {

    private static final MonitoringProperties CONFIG = new MonitoringProperties();

    @Rule
    public MordaMonitoringsRule rule = new MordaMonitoringsRule();

    @Parameterized.Parameters(name = "Traffic block in {0}")
    public static Collection<Object[]> data() throws Exception {
        return ParametrizationConverter.convert(Arrays.asList(
                MOSCOW, KIEV, SANKT_PETERBURG, EKATERINBURG, PERM,
                SAMARA, CHELYABINSK, NOVOSIBIRSK, KAZAN, NIZHNIY_NOVGOROD, VOLGOGRAD, ROSTOV_NA_DONU
        ));
    }

    private Region region;
    private Cleanvars cleanvars;
    private Client client;

    public TrafficTest(Region region) throws IOException {
        this.region = region;
        this.client = MordaClient.getJsonEnabledClient();

        MordaClient mordaClient = new MordaClient(CONFIG.getMordaEnv(), region.getDomain());
        mordaClient.rapidoActions(client)
                .get("traffic", new CookieHeader(new Cookie(CookieName.
                        YANDEX_GID, region.getRegionId())));

        mordaClient.tuneActions(client).setRegion(region);

        String response = mordaClient
                .rapidoActions(client)
                .getResponse("traffic", null, null, null, null)
                .readEntity(String.class);

        this.cleanvars = MordaClient.getObjectMapper().readValue(response, Cleanvars.class);

        rule.addMeta("json", response);
    }

    @Test
    public void trafficIsShown() {
        shouldHaveParameter("Пробки отсутствуют в " + region.getName(),
                cleanvars.getTraffic(), having(on(Traffic.class).getProcessed(), equalTo(1)));

        shouldHaveParameter("Пробки отсутствуют в " + region.getName(),
                cleanvars.getTraffic(), having(on(Traffic.class).getShow(), equalTo(1)));
    }

    @Test
    public void trafficRate() throws IOException {
        ifTrafficShown();

        shouldHaveParameter(cleanvars.getTraffic(), having(on(Traffic.class).getRate(),
                allOf(greaterThanOrEqualTo(0), lessThanOrEqualTo(10))));
        shouldHaveParameter(cleanvars.getTraffic(), having(on(Traffic.class).getRateaccus(),
                not(isEmptyOrNullString())));
    }

    @Test
    public void trafficResponse() throws IOException {
        ifTrafficShown();

        shouldHaveParameter(cleanvars.getTraffic(), having(on(Traffic.class).getHref(), not(isEmptyOrNullString())));
        shouldHaveResponseCode(client, cleanvars.getTraffic().getHref(), equalTo(HttpURLConnection.HTTP_OK));
    }

    @Test
    public void trafficFuture() throws IOException {
        ifTrafficShown();
        ifFutureEnabled();

        LocalDateTime time = TimeUtils.parseHiddenTime(cleanvars.getHiddenTime());

        for (Future future : cleanvars.getTraffic().getFuture()) {
            time = time.plusHours(1);

            shouldHaveParameter(future, having(on(Future.class).getHour(), equalTo(time.getHourOfDay())));
            shouldHaveParameter(future, having(on(Future.class).getJams(),
                    allOf(greaterThanOrEqualTo(0), lessThanOrEqualTo(10))));
        }
    }

    @Test
    public void trafficFutureCloses() throws IOException {
        ifTrafficShown();
        ifFutureEnabled();
        ifInformerDoesNotExist();

        LocalDateTime time = TimeUtils.parseHiddenTime(cleanvars.getHiddenTime());

        List<Integer> rates = extract(cleanvars.getTraffic().getFuture(), on(Future.class).getJams());
        rates.add(cleanvars.getTraffic().getRate());

        assumeThat("максимальный прогноз <= 3", Collections.max(rates), lessThanOrEqualTo(3));

        if (!cleanvars.getTraffic().getFuture().isEmpty()) {

            shouldHaveParameter(cleanvars.getTraffic(), having(on(Traffic.class).getFutureNext(),
                    notNullValue()));
        } else {
            shouldHaveParameter(cleanvars.getTraffic(), having(on(Traffic.class).getFutureNext(),
                    nullValue()));
        }

        if (time.getHourOfDay() > 12 && time.getHourOfDay() < 23 && cleanvars.getTraffic().getRate() > 0) {
            shouldHaveParameter(cleanvars.getTraffic(), having(on(Traffic.class).getFutureLast(),
                    equalTo(String.valueOf(Math.min(time.getHourOfDay() + 5, 23)))));
        }

    }

    @Test
    public void trafficFutureEnabled() throws IOException {
        ifTrafficShown();

        shouldHaveParameter(cleanvars.getTraffic(), having(on(Traffic.class).getFutureEnabled(),
                equalTo(isFutureEnabled(region) ? 1 : 0)));
    }

    @Test
    public void trafficInformer() throws IOException {
        ifTrafficShown();
        ifInformerExists();

        shouldHaveParameter(cleanvars.getTraffic().getInformer(),
                having(on(Informer.class).getText(), not(isEmptyOrNullString())));
        shouldHaveParameter(cleanvars.getTraffic().getInformer(),
                having(on(Informer.class).getLink(), not(isEmptyOrNullString())));
        shouldHaveResponseCode(client, cleanvars.getTraffic().getInformer().getLink(),
                equalTo(HttpURLConnection.HTTP_OK));
    }

    @Test
    public void trafficFutureEndDay() throws IOException {
        ifTrafficShown();
        ifFutureEnabled();
        ifInformerDoesNotExist();

        List<Integer> rates = extract(cleanvars.getTraffic().getFuture(), on(Future.class).getJams());
        rates.add(cleanvars.getTraffic().getRate());

        assumeThat("максимальный прогноз <= 3", Collections.max(rates), lessThanOrEqualTo(3));

        assumeThat(cleanvars.getTraffic().getFutureNext(), nullValue());
        assumeThat(cleanvars.getTraffic().getFutureLast(), equalTo("23"));

        shouldHaveParameter(cleanvars.getTraffic(), having(on(Traffic.class).getFutureEndDay(), equalTo(1)));
    }

    private void ifTrafficShown() {
        assumeThat("Пробки отсутствуют в " + region.getName(), cleanvars.getTraffic(),
                having(on(Traffic.class).getShow(), equalTo(1)));
    }

    private void ifFutureExists() {
        assumeThat("Прогноз отсутствует в " + region.getName(), cleanvars.getTraffic(),
                having(on(Traffic.class).getFuture(), hasSize(greaterThan(0))));
    }

    private void ifInformerExists() {
        assumeThat("Информер отсутствует в " + region.getName(), cleanvars.getTraffic(),
                having(on(Traffic.class).getInformer(), notNullValue()));
    }

    private void ifInformerDoesNotExist() {
        assumeThat("Информер отсутствует в " + region.getName(), cleanvars.getTraffic(),
                having(on(Traffic.class).getInformer(), nullValue()));
    }

    private void ifCheckDirection() {
        LocalDateTime time = TimeUtils.parseHiddenTime(cleanvars.getHiddenTime());
        assumeFalse("Не проверяем направление около 3:00 и 15:00", skipDirection(time));
    }

    private void ifFutureEnabled() {
        assumeTrue("Прогноз должен быть включен для региона", isFutureEnabled(region));
    }
}
