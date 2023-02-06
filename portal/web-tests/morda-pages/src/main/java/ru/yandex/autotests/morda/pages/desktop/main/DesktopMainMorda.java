package ru.yandex.autotests.morda.pages.desktop.main;

import org.openqa.selenium.WebDriver;
import org.openqa.selenium.remote.DesiredCapabilities;
import ru.yandex.autotests.morda.pages.Morda;
import ru.yandex.autotests.morda.pages.MordaType;
import ru.yandex.autotests.morda.rules.allure.AllureFeatureRule;
import ru.yandex.autotests.morda.steps.NavigationSteps;
import ru.yandex.autotests.morda.steps.TuneSteps;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.rules.proxy.configactions.Header;
import ru.yandex.autotests.mordacommonsteps.rules.proxy.configactions.HeaderAction;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.geobase.regions.GeobaseRegion;

import javax.ws.rs.core.UriBuilder;
import java.net.URI;
import java.util.HashSet;
import java.util.List;

import static java.util.Arrays.asList;
import static org.openqa.selenium.remote.DesiredCapabilities.firefox;
import static ru.yandex.autotests.utils.morda.language.Language.*;
import static ru.yandex.autotests.utils.morda.region.Region.*;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 27/02/15
 */
public class DesktopMainMorda extends Morda<DesktopMainPage> {

    private DesktopMainMorda(String scheme, MordaEnvironment environment, Region region, Language language) {
        super(scheme, environment);
        setRegion(region);
        setLanguage(language);
    }

    public static DesktopMainMorda desktopMain(String scheme, String environment, Region region) {
        return new DesktopMainMorda(scheme,
                new MordaEnvironment("www", environment, true),
                region,
                RU
        );
    }

    public static DesktopMainMorda desktopMain(String scheme, String environment, Region region, Language language) {
        return new DesktopMainMorda(scheme,
                new MordaEnvironment("www", environment, true),
                region,
                language
        );
    }

    public static DesktopMainMorda desktopFamilyMain(String scheme, String environment, Region region) {
        return new DesktopMainMorda(scheme,
                new MordaEnvironment("family", environment, false),
                region,
                RU
        );
    }

    public static DesktopMainMorda desktopFamilyMain(String scheme, String environment, Region region, Language language) {
        return new DesktopMainMorda(scheme,
                new MordaEnvironment("family", environment, false),
                region,
                language
        );
    }

    public static DesktopMainMorda desktopNewMain(String scheme, String environment, Region region) {
        return new DesktopMainMorda(scheme,
                new MordaEnvironment("new", environment, true),
                region,
                RU
        );
    }

    public static DesktopMainMorda desktopNewMain(String scheme, String environment, Region region, Language language) {
        return new DesktopMainMorda(scheme,
                new MordaEnvironment("new", environment, true),
                region,
                language
        );
    }

    public static List<DesktopMainMorda> getDefaulFamilytList(String scheme, String environment) {
        return asList(
                desktopFamilyMain(scheme, environment, MOSCOW, RU),
                desktopFamilyMain(scheme, environment, KIEV, UK),
                desktopFamilyMain(scheme, environment, ASTANA, KK),
                desktopFamilyMain(scheme, environment, KAZAN, RU),
                desktopFamilyMain(scheme, environment, MINSK, BE)
        );
    }

    public static List<DesktopMainMorda> getDefaultList(String scheme, String environment) {
        return asList(
                desktopMain(scheme, environment, MOSCOW, RU),
                desktopMain(scheme, environment, KIEV, UK),
                desktopMain(scheme, environment, ASTANA, KK),
                desktopMain(scheme, environment, KAZAN, RU),
                desktopMain(scheme, environment, MINSK, BE)
        );
    }

    @Override
    public void initialize(WebDriver driver) {
        NavigationSteps.open(driver, getUrl());

        TuneSteps.setRegionWithCookie(driver, getCookieDomain(), region);
        TuneSteps.setLanguageWithCookie(driver, getCookieDomain(), language);
    }

    @Override
    public MordaType getMordaType() {
        return MordaType.D_MAIN;
    }

    @Override
    public MordaAllureBaseRule getRule() {
        return getRule(firefox());
    }

    @Override
    public MordaAllureBaseRule getRule(DesiredCapabilities caps) {
        List<Header> headers = asList(
                new Header("X-Yandex-TestExp", "s3_static"),
                new Header("X-Yandex-TestExpForceDisabled", "1")
        );

        return new MordaAllureBaseRule(caps);
//                .withRule(new AllureFeatureRule(getFeature()))
//                .mergeProxyAction(HeaderAction.class, new HashSet<>(headers));
    }

    @Override
    public DesktopMainPage getPage(WebDriver driver) {
        return new DesktopMainPage(driver);
    }

    @Override
    public URI getUrl() {
        return UriBuilder.fromUri("scheme://{env}yandex{domain}/")
                .scheme(scheme)
                .build(environment.parseEnvironment(), getDomain(region));
    }

    public URI getThemeUrl() {
        return UriBuilder.fromUri(getUrl()).path("themes/").build();
    }

    public URI getEditUrl() {
        return UriBuilder.fromUri(getUrl())
                .queryParam("edit", "1")
                .build();
    }

    @Override
    public URI getPassportUrl(String passportEnv) {
        return UriBuilder.fromUri("https://{passportEnv}.yandex{domain}/")
                .build(passportEnv, getDomain(region));
    }

    @Override
    public URI getTuneUrl(String tuneEnv) {

        return UriBuilder.fromUri("https://{tuneEnv}.yandex{domain}/tune/")
                .build(tuneEnv, getDomain(region));
    }

    @Override
    public URI getTuneUrl() {
        return UriBuilder.fromUri("https://yandex{domain}/tune/")
                .build(getDomain(region));
    }

    @Override
    public URI getSerpUrl() {
        if (environment.getPrefix().contains("family")) {
            return UriBuilder.fromUri("https://yandex{domain}/search").build(getDomain(region));
        } else {
            return UriBuilder.fromUri("https://www.yandex{domain}/search").build(getDomain(region));
        }
    }

    @Override
    public String getCookieDomain() {
        return ".yandex" + getDomain(region);
    }

    @Override
    public String getFeature() {
        return "desktop " + getUrl();
    }

    public String getDomain() {
        return getDomain(this.region);
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
    public String toString() {
        return "desktop " + getUrl() + ", " + region + ", " + language;
    }
}
