package ru.yandex.autotests.morda.pages.desktop.firefox;

import org.openqa.selenium.WebDriver;
import org.openqa.selenium.remote.DesiredCapabilities;
import ru.yandex.autotests.morda.pages.Morda;
import ru.yandex.autotests.morda.pages.MordaType;
import ru.yandex.autotests.morda.rules.allure.AllureFeatureRule;
import ru.yandex.autotests.morda.steps.NavigationSteps;
import ru.yandex.autotests.morda.steps.TuneSteps;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.geobase.regions.GeobaseRegion;

import javax.ws.rs.core.UriBuilder;
import java.net.URI;
import java.util.List;

import static java.util.Arrays.asList;
import static org.openqa.selenium.remote.DesiredCapabilities.firefox;
import static ru.yandex.autotests.utils.morda.language.Language.BE;
import static ru.yandex.autotests.utils.morda.language.Language.KK;
import static ru.yandex.autotests.utils.morda.language.Language.RU;
import static ru.yandex.autotests.utils.morda.language.Language.TR;
import static ru.yandex.autotests.utils.morda.language.Language.UK;
import static ru.yandex.autotests.utils.morda.region.Region.ASTANA;
import static ru.yandex.autotests.utils.morda.region.Region.ISTANBUL;
import static ru.yandex.autotests.utils.morda.region.Region.KIEV;
import static ru.yandex.autotests.utils.morda.region.Region.MINSK;
import static ru.yandex.autotests.utils.morda.region.Region.MOSCOW;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 27/02/15
 */
public class DesktopFirefoxMorda extends Morda<DesktopFirefoxPage> {

    private DesktopFirefoxMorda(String scheme, String environment, Region region,
                                Language language) {
        super(scheme,
                new MordaEnvironment("firefox", environment, false));
        setRegion(region);
        setLanguage(language);
    }

    public static DesktopFirefoxMorda desktopFirefox(String scheme, String environment, Region region,
                                                     Language language) {
        return new DesktopFirefoxMorda(scheme, environment, region, language);
    }

    public static List<DesktopFirefoxMorda> getDefaultList(String scheme, String environment) {
        return asList(
                desktopFirefox(scheme, environment, MOSCOW, RU),
                desktopFirefox(scheme, environment, MINSK, BE),
                desktopFirefox(scheme, environment, ASTANA, KK),
                desktopFirefox(scheme, environment, KIEV, UK),
                desktopFirefox(scheme, environment, ISTANBUL, TR)
        );
    }

    @Override
    public void initialize(WebDriver driver) {
        NavigationSteps.open(driver, getUrl());
        TuneSteps.setRegionWithCookie(driver, getCookieDomain(), region);
//        TuneSteps.setRegionNewTune(driver, getTuneUrl("www-" + getEnvironment().getEnvironment()), getCookieDomain(), region);
//        TuneSteps.setLanguageNewTune(driver, getTuneUrl("www-" + getEnvironment().getEnvironment()), getCookieDomain(), language);
        TuneSteps.setLanguageWithCookie(driver, getCookieDomain(), language);
    }

    @Override
    public MordaType getMordaType() {
        return MordaType.D_FIREFOX;
    }

    @Override
    public MordaAllureBaseRule getRule() {
        return getRule(firefox());
    }

    @Override
    public MordaAllureBaseRule getRule(DesiredCapabilities caps) {
        return new MordaAllureBaseRule(caps)
                .withRule(new AllureFeatureRule(getFeature()));
    }

    @Override
    public DesktopFirefoxPage getPage(WebDriver driver) {
        return new DesktopFirefoxPage(driver);
    }

    @Override
    public URI getUrl() {
        return UriBuilder.fromUri("scheme://{env}yandex{tld}/")
                .scheme(scheme)
                .build(environment.parseEnvironment(), getDomainKUBRT(region));
    }

    @Override
    public URI getPassportUrl(String passportEnv) {
        return UriBuilder.fromUri("https://{passportEnv}.yandex{tld}/")
                .build(passportEnv, getDomainKUBRT(region));
    }

    @Override
    public URI getTuneUrl(String tuneEnv) {
        if (getDomainKUBRT(region).equals(".com.tr")) {
            return UriBuilder.fromUri("https://{tuneEnv}.yandex{tld}/")
                    .build(tuneEnv, getDomainKUBRT(region));
        }
        return UriBuilder.fromUri("https://{tuneEnv}.yandex{tld}/")
                .build(tuneEnv, getDomainKUBRT(region));
    }

    @Override
    public URI getSerpUrl() {
        return UriBuilder.fromUri("{scheme}://yandex{tld}/search/")
                .build(scheme, getDomainKUBRT(region));
    }

    @Override
    public String getCookieDomain() {
        return String.format(".yandex%s", getDomainKUBRT(region));
    }

    @Override
    public String getFeature() {
        return "desktop " + getUrl();
    }

    public String getTld() {
        return getDomainKUBRT(region);
    }

    private String getDomainKUBRT(Region region) {
        int by = 149;
        int kz = 159;
        int ua = 187;
        int comtr = 983;
        List<Integer> parents = new GeobaseRegion(region.getRegionIdInt()).getParentsIds();
        if (parents.contains(by)) {
            return ".by";
        } else if (parents.contains(kz)) {
            return ".kz";
        } else if (parents.contains(ua)) {
            return ".ua";
        } else if (parents.contains(comtr)) {
            return ".com.tr";
        }
        return ".ru";
    }

    public String getDomainKUBRT() {
        return getDomainKUBRT(region);
    }

    @Override
    public String toString() {
        return String.format("desktop %s, %s, %s", getUrl(), region, language);
    }
}
