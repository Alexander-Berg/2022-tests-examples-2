package ru.yandex.autotests.morda.pages.desktop.smarttv;

import org.openqa.selenium.WebDriver;
import org.openqa.selenium.remote.DesiredCapabilities;
import ru.yandex.autotests.morda.pages.Morda;
import ru.yandex.autotests.morda.pages.MordaType;
import ru.yandex.autotests.morda.rules.allure.AllureFeatureRule;
import ru.yandex.autotests.morda.steps.TuneSteps;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.rules.proxy.configactions.UserAgentAction;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.geobase.regions.GeobaseRegion;

import javax.ws.rs.core.UriBuilder;
import java.net.URI;
import java.util.List;

import static ru.yandex.autotests.morda.pages.MordaType.SMART_TV;
import static ru.yandex.autotests.morda.steps.NavigationSteps.open;
import static ru.yandex.autotests.utils.morda.language.Language.RU;
import static ru.yandex.autotests.utils.morda.region.Region.MOSCOW;

/**
 * User: asamar
 * Date: 18.11.16
 */
public class SmartTvMorda extends Morda<SmartTvPage> {
    private String userAgent;

    public static SmartTvMorda smartTvMorda(String scheme, String environment, String userAgent) {
        return new SmartTvMorda(scheme,
                new MordaEnvironment("www", environment, true),
                userAgent,
                MOSCOW);
    }

    public static SmartTvMorda smartTvMorda(String scheme, String environment, String userAgent, Region region) {
        return new SmartTvMorda(scheme,
                new MordaEnvironment("www", environment, true),
                userAgent,
                region);
    }

    public SmartTvMorda(String scheme, MordaEnvironment environment, String userAgent, Region region) {
        super(scheme, environment);
        setRegion(region);
        setLanguage(RU);
        this.userAgent = userAgent;
    }

    @Override
    public void initialize(WebDriver driver) {
        open(driver, getUrl());
        TuneSteps.setRegionWithCookie(driver, getCookieDomain(), region);
        TuneSteps.setLanguageWithCookie(driver, getCookieDomain(), language);
    }

    @Override
    public MordaType getMordaType() {
        return SMART_TV;
    }

    @Override
    public MordaAllureBaseRule getRule(DesiredCapabilities caps) {

        return new MordaAllureBaseRule(caps)
                .withRule(new AllureFeatureRule(getFeature()))
                .replaceProxyAction(UserAgentAction.class, userAgent);
    }

    @Override
    public SmartTvPage getPage(WebDriver driver) {
        return new SmartTvPage(driver);
    }

    @Override
    public URI getUrl() {
        return UriBuilder.fromUri("scheme://{env}yandex{domain}/")
                .scheme(scheme)
                .build(environment.parseEnvironment(), getDomain(region));
    }

    @Override
    public URI getPassportUrl(String passportEnv) {
        return URI.create("https://passport.yandex.ru/");
    }

    @Override
    public URI getTuneUrl(String tuneEnv) {
        return URI.create("https://tune.yandex.ru/");
    }

    @Override
    public URI getSerpUrl() {
        return URI.create("https://yandex.ru/search");
    }

    @Override
    public String getCookieDomain() {
        return ".yandex" + getDomain(region);
    }

    @Override
    public String getFeature() {
        return "smart tv " + getUrl();
    }

    @Override
    public String toString() {
        return "smart tv " + getUrl() + ", " + getRegion() + ", " + getLanguage();
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
}
