package ru.yandex.autotests.morda.pages.touch.spok;

import org.openqa.selenium.WebDriver;
import org.openqa.selenium.remote.DesiredCapabilities;
import ru.yandex.autotests.morda.pages.Morda;
import ru.yandex.autotests.morda.pages.MordaType;
import ru.yandex.autotests.morda.rules.allure.AllureFeatureRule;
import ru.yandex.autotests.morda.steps.NavigationSteps;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.rules.proxy.configactions.UserAgentAction;

import javax.ws.rs.core.UriBuilder;
import java.net.URI;
import java.util.List;
import java.util.stream.Collectors;

import static java.util.Arrays.asList;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 27/02/15
 */
public class TouchSpokMorda extends Morda<Object> {

    private String domain;
    private String userAgent;

    private TouchSpokMorda(String scheme, MordaEnvironment environment, String domain, String userAgent) {
        super(scheme, environment);
        this.domain = domain;
        this.userAgent = userAgent;
    }

    public static TouchSpokMorda touchSpok(String domain, String userAgent) {
        return touchSpok("production", domain, userAgent);
    }

    public static TouchSpokMorda touchSpok(String environment, String domain, String userAgent) {
        return touchSpok("https", environment, domain, userAgent);
    }

    public static TouchSpokMorda touchSpok(String scheme, String environment, String domain, String userAgent) {
        return new TouchSpokMorda(scheme, new MordaEnvironment("www", environment, false), domain, userAgent);
    }

    public static List<TouchSpokMorda> getDefaultList(String environment, String userAgent) {
        List<String> domains = asList(".az", ".com.am", ".co.il", ".kg", ".lv",
                ".md", ".tj", ".tm", ".ee", ".lt", ".fr");
        return domains.stream()
                .map(d -> touchSpok(environment, d, userAgent))
                .collect(Collectors.toList());
    }

    @Override
    public void initialize(WebDriver driver) {
        NavigationSteps.open(driver, getUrl());
    }

    @Override
    public MordaType getMordaType() {
        return MordaType.T_SPOK;
    }

    @Override
    public MordaAllureBaseRule getRule(DesiredCapabilities caps) {
        return new MordaAllureBaseRule(caps)
                .replaceProxyAction(UserAgentAction.class, userAgent)
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
        return "touch " + getUrl();
    }

    @Override
    public String toString() {
        return "desktop " + getUrl();
    }
}
