package ru.yandex.autotests.mordabackend.firefox.traffic;

import org.joda.time.LocalDateTime;
import org.junit.Test;
import org.junit.runner.RunWith;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mordabackend.MordaClient;
import ru.yandex.autotests.mordabackend.Properties;
import ru.yandex.autotests.mordabackend.beans.cleanvars.Cleanvars;
import ru.yandex.autotests.mordabackend.beans.traffic.Traffic;
import ru.yandex.autotests.mordabackend.useragents.UserAgent;
import ru.yandex.autotests.mordabackend.utils.TimeUtils;
import ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils;
import ru.yandex.autotests.mordabackend.utils.runner.CleanvarsParametrizedRunner;
import ru.yandex.autotests.mordaexportsclient.MordaExports;
import ru.yandex.autotests.mordaexportsclient.beans.TrafficMobileEntry;
import ru.yandex.autotests.utils.morda.BaseProperties;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.autotests.utils.morda.url.Domain;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import javax.ws.rs.client.Client;
import java.io.IOException;

import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.on;
import static org.hamcrest.Matchers.*;
import static org.junit.Assume.assumeFalse;
import static org.junit.Assume.assumeThat;
import static ru.yandex.autotests.mordabackend.blocks.CleanvarsBlock.HIDDENTIME;
import static ru.yandex.autotests.mordabackend.blocks.CleanvarsBlock.TRAFFIC;
import static ru.yandex.autotests.mordabackend.traffic.TrafficUtils.*;
import static ru.yandex.autotests.mordabackend.useragents.UserAgent.FF_34;
import static ru.yandex.autotests.mordabackend.useragents.UserAgent.PDA;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.shouldHaveParameter;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.shouldHaveResponseCode;
import static ru.yandex.autotests.mordabackend.utils.LinkUtils.addLink;
import static ru.yandex.autotests.mordabackend.utils.LinkUtils.normalizeUrl;
import static ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils.parameters;
import static ru.yandex.autotests.mordaexportslib.ExportProvider.export;
import static ru.yandex.autotests.mordaexportslib.matchers.GeoMatcher.geo;
import static ru.yandex.autotests.mordaexportslib.matchers.LangMatcher.lang;
import static ru.yandex.autotests.mordaexportslib.matchers.MordatypeMatcher.mordatype;
import static ru.yandex.autotests.utils.morda.url.Domain.*;

/**
 * User: ivannik
 * Date: 21.07.2014
 */
@Aqua.Test(title = "Firefox Traffic Block")
@Features("Firefox")
@Stories("Firefox Traffic Block")
@RunWith(CleanvarsParametrizedRunner.class)
public class FirefoxTrafficTest {
    private static final Properties CONFIG = new Properties();

    @CleanvarsParametrizedRunner.Parameters("{3}, {4}, {5}")
    public static ParametersUtils parameters =
            parameters(new BaseProperties.MordaEnv(CONFIG.getMordaEnv().getEnv().replace("www-", "firefox-")),
                    RU, UA, COM_TR)
                    .withLanguages(Language.RU, Language.UK, Language.BE, Language.KK, Language.TT)
                    .withUserAgents(FF_34)
                    .withLanguages(LANGUAGES)
                    .withCleanvarsBlocks(TRAFFIC, HIDDENTIME);

    private Client client;
    private Region region;
    private Language language;
    private UserAgent userAgent;
    private Cleanvars cleanvars;
    private TrafficMobileEntry trafficMobileEntry;
//    private TrafinfoEntry trafinfoEntry;

    public FirefoxTrafficTest(MordaClient mordaClient, Client client, Cleanvars cleanvars,
                              Region region, Language language, UserAgent userAgent) {
        this.client = client;
        this.region = region;
        this.language = language;
        this.userAgent = userAgent;
        this.cleanvars = cleanvars;
        this.trafficMobileEntry =
                export(MordaExports.TRAFFIC_MOBILE, mordatype(region.getDomain()),
                        lang(language), geo(region.getRegionIdInt()));
//        this.trafinfoEntry = export(MordaExports.TRAFINFO,
//                having(on(TrafinfoEntry.class).getFrom(),
//                        before("yyyy-MM-dd HH:mm", "yyyy-MM-dd HH:mm:ss", cleanvars.getHiddenTime())),
//                having(on(TrafinfoEntry.class).getTill(),
//                        after("yyyy-MM-dd HH:mm", "yyyy-MM-dd HH:mm:ss", cleanvars.getHiddenTime())),
//                domain(region.getDomain()), lang(language), geo(region.getRegionIdInt()));
    }

    @Test
    public void colorClass() {
        assumeThat(cleanvars.getTraffic().getRate(), notNullValue());
        shouldHaveParameter(cleanvars.getTraffic(), having(on(Traffic.class).getClazz(),
                equalTo(COLOR_CLASSES.get(cleanvars.getTraffic().getRate()))));
    }

    @Test
    public void future() {
        if (isFutureEnabled(region)) {
            shouldHaveParameter(cleanvars.getTraffic(), having(on(Traffic.class).getFutureEnabled(), equalTo(1)));
            shouldHaveFuture(cleanvars.getTraffic());
        } else {
            shouldHaveParameter(cleanvars.getTraffic(), having(on(Traffic.class).getFutureEnabled(), equalTo(0)));
            shouldHaveParameter(cleanvars.getTraffic(), having(on(Traffic.class).getFuture(), empty()));
        }
    }

//    @Test
    public void direction() {
        assumeThat(cleanvars.getTraffic().getRate(), notNullValue());

        LocalDateTime time = TimeUtils.parseHiddenTime(cleanvars.getHiddenTime());
        assumeFalse("Не проверяем направление около 3:00 и 15:00", skipDirection(time));

        shouldHaveParameter(cleanvars.getTraffic(), having(on(Traffic.class).getDirection(),
                getDirectionMatcher(time)));
    }

    @Test
    public void trafficHref() throws IOException {
        assumeThat(cleanvars.getTraffic().getRate(), notNullValue());
        if (userAgent.equals(PDA) && region.getDomain().equals(Domain.COM_TR)) {
            shouldHaveParameter(cleanvars.getTraffic(), having(on(Traffic.class).getHref(), isEmptyString()));
        } else {
            shouldHaveParameter(cleanvars.getTraffic(), having(on(Traffic.class).getHref(),
                    region.getDomain().equals(COM_TR) ?
                            anyOf(equalTo("http://m.soft.yandex.com.tr/maps/"),
                                    containsString("trafik"), containsString("trf"), containsString("traffic")) :
                            allOf(containsString("yandex."), containsString("/maps"), containsString("/probki"))
            ));
            addLink(cleanvars.getTraffic().getHref(), region, false, language, userAgent);
            shouldHaveResponseCode(client, normalizeUrl(cleanvars.getTraffic().getHref()), userAgent, equalTo(200));
        }
    }

//    @Test
    public void descriptionOrInfo() throws IOException {
        assumeThat(cleanvars.getTraffic().getRate(), notNullValue());
        assumeThat("Description hided", cleanvars.getTraffic().getFutureHideDescription(), equalTo(0));
//        shouldHaveDescriptionOrInfo(trafinfoEntry, cleanvars, client, region, language, userAgent);
    }

    @Test
    public void mobileUrl() throws IOException {
        assumeThat(cleanvars.getTraffic().getRate(), notNullValue());
        shouldHaveParameter(cleanvars.getTraffic(), having(on(Traffic.class).getMobile().getUrl(),
                equalTo(trafficMobileEntry.getUrl())));
        addLink(cleanvars.getTraffic().getMobile().getUrl(), region, false, language, userAgent);
        shouldHaveResponseCode(client, cleanvars.getTraffic().getMobile().getUrl(), userAgent, equalTo(200));
    }

    @Test
    public void mobileLinkid() {
        assumeThat(cleanvars.getTraffic().getRate(), notNullValue());
        shouldHaveParameter(cleanvars.getTraffic(), having(on(Traffic.class).getMobile().getLinkid(),
                equalTo(trafficMobileEntry.getLinkid())));
    }

    @Test
    public void showFlag() {
        if (cleanvars.getTraffic().getRate() != null) {
            shouldHaveParameter(cleanvars.getTraffic(), having(on(Traffic.class).getShow(), equalTo(1)));
        } else {
            shouldHaveParameter(cleanvars.getTraffic(), having(on(Traffic.class).getShow(), equalTo(0)));
        }
    }

    @Test
    public void processedFlag() {
        shouldHaveParameter(cleanvars.getTraffic(), having(on(Traffic.class).getProcessed(), equalTo(1)));
    }
}
