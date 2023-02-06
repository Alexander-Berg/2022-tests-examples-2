package ru.yandex.autotests.morda.pages.touch.ru;

import org.openqa.selenium.WebDriver;
import org.openqa.selenium.remote.DesiredCapabilities;
import ru.yandex.autotests.morda.pages.Morda;
import ru.yandex.autotests.morda.pages.MordaType;
import ru.yandex.autotests.morda.rules.allure.AllureFeatureRule;
import ru.yandex.autotests.morda.steps.MordaSteps;
import ru.yandex.autotests.morda.steps.TuneSteps;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.rules.proxy.actions.HarAction;
import ru.yandex.autotests.mordacommonsteps.rules.proxy.configactions.Header;
import ru.yandex.autotests.mordacommonsteps.rules.proxy.configactions.HeaderAction;
import ru.yandex.autotests.mordacommonsteps.rules.proxy.configactions.UserAgentAction;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.geobase.regions.GeobaseRegion;

import javax.ws.rs.core.UriBuilder;
import java.net.URI;
import java.util.HashSet;
import java.util.List;

import static java.util.Arrays.asList;
import static javax.ws.rs.core.UriBuilder.fromUri;
import static org.openqa.selenium.remote.DesiredCapabilities.firefox;
import static ru.yandex.autotests.morda.steps.NavigationSteps.open;
import static ru.yandex.autotests.utils.morda.language.Language.BE;
import static ru.yandex.autotests.utils.morda.language.Language.KK;
import static ru.yandex.autotests.utils.morda.language.Language.RU;
import static ru.yandex.autotests.utils.morda.language.Language.UK;
import static ru.yandex.autotests.utils.morda.region.Region.ASTANA;
import static ru.yandex.autotests.utils.morda.region.Region.HARKOV;
import static ru.yandex.autotests.utils.morda.region.Region.KIEV;
import static ru.yandex.autotests.utils.morda.region.Region.MINSK;
import static ru.yandex.autotests.utils.morda.region.Region.MOSCOW;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 27/02/15
 */
public class TouchRuMorda extends Morda<TouchRuPage> {
    private String userAgent;
    private String lat;
    private String lon;

    public TouchRuMorda(String scheme, MordaEnvironment environment, String userAgent, Region region,
                        Language language) {
        super(scheme, environment);
        setRegion(region);
        setLanguage(language);
        this.userAgent = userAgent;
    }

    public TouchRuMorda(String scheme, MordaEnvironment environment, String userAgent, Region region, String lat, String lon,
                        Language language) {
        super(scheme, environment);
        setLanguage(language);
        setRegion(region);
        this.userAgent = userAgent;
        this.lat = lat;
        this.lon = lon;
    }

    public static TouchRuMorda touchRu(String scheme, String environment, String userAgent, Region region,
                                       Language language) {
        return new TouchRuMorda(scheme,
                new MordaEnvironment("www", environment, false),
                userAgent,
                region,
                language
        );
    }

    public static TouchRuMorda touchRu(String scheme, String environment, String userAgent, Region region, String lat, String lon,
                                       Language language) {
        return new TouchRuMorda(scheme,
                new MordaEnvironment("www", environment, false),
                userAgent,
                region,
                lat,
                lon,
                language
        );
    }

    public static List<TouchRuMorda> getDefaultList(String scheme, String environment, String userAgent) {
        return asList(
//                touchRu(scheme, environment, userAgent, MOSCOW, RU),
                touchRu(scheme, environment, userAgent, KIEV, UK)
//                touchRu(scheme, environment, userAgent, HARKOV, RU),
//                touchRu(scheme, environment, userAgent, MINSK, BE),
//                touchRu(scheme, environment, userAgent, ASTANA, KK)
        );
    }

    @Override
    public MordaType getMordaType() {
        return MordaType.T_RU;
    }

    @Override
    public MordaAllureBaseRule getRule() {
        return getRule(firefox());
    }

    @Override
    public MordaAllureBaseRule getRule(DesiredCapabilities caps) {
        List<Header> headers = asList(
//                new Header("X-Yandex-TestExp", "geotuning2"),
                new Header("X-Yandex-TestExpForceDisabled", "1"),
                new Header("X-Yandex-TestCounters", "0")
        );
        return new MordaAllureBaseRule(caps)
                .withRule(new AllureFeatureRule(getFeature()))
                .replaceProxyAction(UserAgentAction.class, userAgent)
                .withProxyAction(new HarAction("asfasfa"))
                .mergeProxyAction(HeaderAction.class, new HashSet<>(headers));
    }

    @Override
    public TouchRuPage getPage(WebDriver driver) {
        return new TouchRuPage(driver);
    }

    @Override
    public URI getUrl() {
        return UriBuilder.fromUri("scheme://{env}yandex{domain}/")
                .scheme(scheme)
                .build(environment.parseEnvironment(), getDomain(region));
    }

    @Override
    public URI getPassportUrl(String passportEnv) {
        return UriBuilder.fromUri("https://{passportEnv}.yandex{domain}/")
                .build(passportEnv, getDomain(region));
    }

    @Override
    public URI getTuneUrl(String tuneEnv) {
        return UriBuilder.fromUri("https://{tuneEnv}.yandex.ru/")
                .build(tuneEnv);
    }

    @Override
    public URI getSerpUrl() {
        return UriBuilder.fromUri("{scheme}://yandex.ru/touchsearch")
                .build(scheme);
    }

    @Override
    public void initialize(WebDriver driver) {
        URI withMda = fromUri(getUrl()).queryParam("mda","0").build();
        open(driver, withMda);

        TuneSteps.setRegionWithCookie(driver, getCookieDomain(), region);

        if (lat != null && lon != null) {
            MordaSteps.setCoordinates(driver, withMda, getCookieDomain(), lat, lon);
        }

        TuneSteps.setLanguageWithCookie(driver, getCookieDomain(), language);
        open(driver, getUrl());
    }

    @Override
    public String getCookieDomain() {
        return ".yandex" + getDomain(region);
    }

    private String getDomain(Region region) {
        int by = 149;
        int kz = 159;
        int ua = 187;
        List<Integer> parents = new GeobaseRegion(region.getRegionIdInt()).getParentsIds();
        if (parents.contains(by)) {
            return ".by";
        } else if (parents.contains(kz)) {
            return ".kz";
        } else if (parents.contains(ua)) {
            return ".ua";
        }
        return ".ru";
    }

    @Override
    public String getFeature() {
        return "touch " + getUrl();
    }

    @Override
    public String toString() {
        return "touch " + getUrl() + ", " + getRegion() + ", " + getLanguage();
    }
}
