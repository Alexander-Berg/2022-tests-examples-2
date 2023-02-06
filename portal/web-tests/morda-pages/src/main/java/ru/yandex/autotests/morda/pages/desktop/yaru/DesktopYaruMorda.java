package ru.yandex.autotests.morda.pages.desktop.yaru;

import org.openqa.selenium.WebDriver;
import org.openqa.selenium.remote.DesiredCapabilities;
import ru.yandex.autotests.morda.pages.Morda;
import ru.yandex.autotests.morda.pages.MordaType;
import ru.yandex.autotests.morda.rules.allure.AllureFeatureRule;
import ru.yandex.autotests.morda.steps.NavigationSteps;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.rules.proxy.configactions.RemapAction;
import ru.yandex.autotests.utils.morda.language.Language;

import javax.ws.rs.core.UriBuilder;
import java.net.URI;
import java.util.HashMap;
import java.util.Map;
import java.util.regex.Pattern;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 27/02/15
 */
public class DesktopYaruMorda extends Morda<DesktopYaruPage> {

    private DesktopYaruMorda(String scheme, MordaEnvironment environment) {
        super(scheme, environment);
        setLanguage(Language.RU);
    }

    @Override
    public MordaType getMordaType() {
        return MordaType.D_YARU;
    }

    public static DesktopYaruMorda desktopYaru(String scheme, String environment) {
        return new DesktopYaruMorda(scheme,
                new MordaEnvironment("", environment, false)
        );
    }

    @Override
    public void initialize(WebDriver driver) {
        NavigationSteps.open(driver, getUrl());
    }

    @Override
    public MordaAllureBaseRule getRule(DesiredCapabilities caps) {
        MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule(caps)
                .withRule(new AllureFeatureRule(getFeature()));

        if (getEnvironment().getEnvironment().equals("rc")) {
            Map<Pattern, String> remap = new HashMap<>();
            remap.put(Pattern.compile("ya\\.ru"), "178.154.225.1");
            mordaAllureBaseRule.mergeProxyAction(RemapAction.class, remap);
        }

        return mordaAllureBaseRule;
    }

    @Override
    public DesktopYaruPage getPage(WebDriver driver) {
        return new DesktopYaruPage(driver);
    }

    @Override
    public URI getUrl() {
        if (environment.getEnvironment().equals("rc") || environment.getEnvironment().equals("production")) {
            return UriBuilder.fromUri("scheme://ya.ru/")
                    .scheme(scheme)
                    .build();
        }

        return UriBuilder.fromUri("scheme://{env}.ya.ru/")
                .scheme(scheme)
                .build(environment.getEnvironment());
    }

    @Override
    public URI getPassportUrl(String passportEnv) {
        return UriBuilder.fromUri("https://{passportEnv}.yandex.ru/")
                .build(passportEnv);
    }

    @Override
    public URI getTuneUrl(String tuneEnv) {
        return UriBuilder.fromUri("https://{tuneEnv}.yandex.ru/")
                .build(tuneEnv);
    }

    @Override
    public URI getSerpUrl() {
        return UriBuilder.fromUri("scheme://yandex.ru/search/")
                .scheme(scheme)
                .build();
    }

    @Override
    public String getCookieDomain() {
        return ".ya.ru";
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
