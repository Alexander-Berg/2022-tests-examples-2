package ru.yandex.autotests.morda.pages.pda.yaru;

import org.openqa.selenium.WebDriver;
import org.openqa.selenium.remote.DesiredCapabilities;
import ru.yandex.autotests.morda.pages.Morda;
import ru.yandex.autotests.morda.pages.MordaType;
import ru.yandex.autotests.morda.rules.allure.AllureFeatureRule;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.rules.proxy.configactions.RemapAction;
import ru.yandex.autotests.mordacommonsteps.rules.proxy.configactions.UserAgentAction;

import javax.ws.rs.core.UriBuilder;
import java.net.URI;
import java.util.HashMap;
import java.util.Map;
import java.util.regex.Pattern;

import static org.openqa.selenium.remote.DesiredCapabilities.firefox;
import static ru.yandex.autotests.morda.steps.NavigationSteps.open;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 27/02/15
 */
public class PdaYaRuMorda extends Morda<PdaYaRuPage> {
    private String userAgent;

    public PdaYaRuMorda(String scheme, MordaEnvironment environment, String userAgent) {
        super(scheme, environment);
        this.userAgent = userAgent;
    }

    public static PdaYaRuMorda pdaYaRu(String scheme, String environment, String userAgent) {
        return new PdaYaRuMorda(scheme,
                new MordaEnvironment("www", environment, false),
                userAgent
        );
    }

    @Override
    public MordaType getMordaType() {
        return MordaType.P_YARU;
    }

    @Override
    public MordaAllureBaseRule getRule() {
        return getRule(firefox());
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

        return mordaAllureBaseRule
                .replaceProxyAction(UserAgentAction.class, userAgent);
    }

    @Override
    public PdaYaRuPage getPage(WebDriver driver) {
        return new PdaYaRuPage(driver);
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
        return UriBuilder.fromUri("{scheme}://yandex.ru/msearch")
                .build(scheme);
    }

    @Override
    public void initialize(WebDriver driver) {
        open(driver, getUrl());
    }

    @Override
    public String getCookieDomain() {
        return ".yandex.ru";
    }

    @Override
    public String getFeature() {
        return "pda " + getUrl();
    }

    @Override
    public String toString() {
        return "pda " + getUrl();
    }
}
