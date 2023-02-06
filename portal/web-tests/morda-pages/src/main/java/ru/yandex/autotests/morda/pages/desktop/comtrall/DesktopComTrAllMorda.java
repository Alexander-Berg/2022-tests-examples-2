package ru.yandex.autotests.morda.pages.desktop.comtrall;

import org.openqa.selenium.WebDriver;
import org.openqa.selenium.remote.DesiredCapabilities;
import ru.yandex.autotests.morda.pages.Morda;
import ru.yandex.autotests.morda.pages.MordaType;
import ru.yandex.autotests.morda.rules.allure.AllureFeatureRule;
import ru.yandex.autotests.morda.steps.NavigationSteps;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;

import javax.ws.rs.core.UriBuilder;
import java.net.URI;

import static org.openqa.selenium.remote.DesiredCapabilities.firefox;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 27/02/15
 */
public class DesktopComTrAllMorda extends Morda<DesktopComTrAllPage> {

    private DesktopComTrAllMorda(String scheme, MordaEnvironment environment) {
        super(scheme, environment);
    }

    @Override
    public MordaType getMordaType() {
        return MordaType.D_COMTRALL;
    }

    public static DesktopComTrAllMorda desktopComTrAll(String scheme, String environment) {
        return new DesktopComTrAllMorda(scheme,
                new MordaEnvironment("www", environment, false)
        );
    }

    public static DesktopComTrAllMorda desktopFamilyComTrAll(String scheme, String environment) {
        return new DesktopComTrAllMorda(scheme,
                new MordaEnvironment("aile", environment, false)
        );
    }

    @Override
    public void initialize(WebDriver driver) {
        NavigationSteps.open(driver, getUrl());
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
    public DesktopComTrAllPage getPage(WebDriver driver) {
        return new DesktopComTrAllPage(driver);
    }

    @Override
    public URI getUrl() {
        return UriBuilder.fromUri("scheme://{env}yandex.com.tr/all")
                .scheme(scheme)
                .build(environment.parseEnvironment());
    }

    @Override
    public URI getPassportUrl(String passportEnv) {
        return UriBuilder.fromUri("https://{passportEnv}.yandex.com.tr/")
                .build(passportEnv);
    }

    @Override
    public URI getTuneUrl(String tuneEnv) {
        return UriBuilder.fromUri("https://{tuneEnv}.yandex.com.tr/")
                .build(tuneEnv);
    }

    @Override
    public URI getSerpUrl() {
        return UriBuilder.fromUri("https://{prefix}.yandex.com.tr/yandsearch")
                .build(environment.getPrefix());
    }

    @Override
    public String getCookieDomain() {
        return ".yandex.com.tr";
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
