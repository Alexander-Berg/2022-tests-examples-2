package ru.yandex.autotests.morda.pages.desktop.spok;

import org.openqa.selenium.WebDriver;
import org.openqa.selenium.remote.DesiredCapabilities;
import ru.yandex.autotests.morda.pages.Morda;
import ru.yandex.autotests.morda.pages.MordaType;
import ru.yandex.autotests.morda.rules.allure.AllureFeatureRule;
import ru.yandex.autotests.morda.steps.NavigationSteps;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;

import javax.ws.rs.core.UriBuilder;
import java.net.URI;
import java.util.List;
import java.util.stream.Collectors;

import static java.util.Arrays.asList;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 27/02/15
 */
public class DesktopSpokMorda extends Morda<Object> {

    private String domain;

    private DesktopSpokMorda(String scheme, MordaEnvironment environment, String domain) {
        super(scheme, environment);
        this.domain = domain;
    }

    public static DesktopSpokMorda desktopSpok(String domain) {
        return desktopSpok("production", domain);
    }

    public static DesktopSpokMorda desktopSpok(String environment, String domain) {
        return desktopSpok("https", environment, domain);
    }

    public static DesktopSpokMorda desktopSpok(String scheme, String environment, String domain) {
        return new DesktopSpokMorda(scheme, new MordaEnvironment("www", environment, false), domain);
    }

    public static List<DesktopSpokMorda> getDefaultList(String environment) {
        List<String> domains = asList(".az", ".com.am", ".co.il", ".kg", ".lv",
                ".md", ".tj", ".tm", ".ee", ".lt", ".fr");
        return domains.stream()
                .map(d -> desktopSpok(environment, d))
                .collect(Collectors.toList());
    }

    @Override
    public void initialize(WebDriver driver) {
        NavigationSteps.open(driver, getUrl());
    }

    @Override
    public MordaType getMordaType() {
        return MordaType.D_SPOK;
    }

    @Override
    public MordaAllureBaseRule getRule(DesiredCapabilities caps) {
        return new MordaAllureBaseRule(caps)
                .withRule(new AllureFeatureRule(getFeature()));
    }

    @Override
    public Object getPage(WebDriver driver) {
        return null;
    }

    @Override
    public URI getUrl() {
        return UriBuilder.fromUri("scheme://{env}yandex{domain}/")
                .scheme(getScheme())
                .build(getEnvironment().parseEnvironment(), domain);
    }

    @Override
    public URI getPassportUrl(String passportEnv) {
        return null;
    }

    @Override
    public URI getTuneUrl(String tuneEnv) {
        return null;
    }

    @Override
    public URI getSerpUrl() {
        return null;
    }

    @Override
    public String getCookieDomain() {
        return null;
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
