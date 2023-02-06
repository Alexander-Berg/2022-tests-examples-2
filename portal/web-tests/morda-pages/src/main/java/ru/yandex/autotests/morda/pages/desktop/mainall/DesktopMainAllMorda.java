package ru.yandex.autotests.morda.pages.desktop.mainall;

import org.openqa.selenium.WebDriver;
import org.openqa.selenium.remote.DesiredCapabilities;
import ru.yandex.autotests.morda.pages.Morda;
import ru.yandex.autotests.morda.pages.MordaType;
import ru.yandex.autotests.morda.rules.allure.AllureFeatureRule;
import ru.yandex.autotests.morda.steps.NavigationSteps;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.utils.morda.region.Region;

import javax.ws.rs.core.UriBuilder;
import java.net.URI;

import static org.openqa.selenium.remote.DesiredCapabilities.firefox;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 27/02/15
 */
public class DesktopMainAllMorda extends Morda<DesktopMainAllPage> {
    private int geoId;

    private DesktopMainAllMorda(String scheme, MordaEnvironment environment, Region region) {
        super(scheme, environment);
        setRegion(region);
    }

    public static DesktopMainAllMorda desktopMainAll(String scheme, String environment, Region region) {
        return new DesktopMainAllMorda(scheme,
                new MordaEnvironment("www", environment, true),
                region
        );
    }

    public static DesktopMainAllMorda desktopFamilyMainAll(String scheme, String environment, Region region) {
        return new DesktopMainAllMorda(scheme,
                new MordaEnvironment("family", environment, false),
                region
        );
    }

    @Override
    public void initialize(WebDriver driver) {
        NavigationSteps.open(driver, getUrl());
    }

    @Override
    public MordaType getMordaType() {
        return MordaType.D_MAINALL;
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
    public DesktopMainAllPage getPage(WebDriver driver) {
        return new DesktopMainAllPage(driver);
    }

    @Override
    public URI getUrl() {
        //todo: get domain for geoId
        return UriBuilder.fromUri("scheme://{env}yandex{domain}/all")
                .scheme(scheme)
                .build(environment.parseEnvironment(), region.getDomain());
    }

    @Override
    public URI getPassportUrl(String passportEnv) {
        //todo: get domain for geoId
        return UriBuilder.fromUri("https://{passportEnv}.yandex.ru/")
                .build(passportEnv);
    }

    @Override
    public URI getTuneUrl(String tuneEnv) {
        //todo: get domain for geoId
        return UriBuilder.fromUri("https://{tuneEnv}.yandex.ru/")
                .build(tuneEnv);
    }

    @Override
    public URI getSerpUrl() {
        //todo: get domain for geoId
        return UriBuilder.fromUri("https://yandex.ru/yandsearch").build();
    }

    @Override
    public String getCookieDomain() {
        //todo: get domain for geoId
        return ".yandex.ru";
    }

    @Override
    public String getFeature() {
        return "desktop " + getUrl();
    }

    @Override
    public String toString() {
        return "desktop " + getUrl();
    }
}
