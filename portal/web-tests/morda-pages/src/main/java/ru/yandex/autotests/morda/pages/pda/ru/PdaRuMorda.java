package ru.yandex.autotests.morda.pages.pda.ru;

import org.openqa.selenium.WebDriver;
import org.openqa.selenium.remote.DesiredCapabilities;
import ru.yandex.autotests.morda.pages.Morda;
import ru.yandex.autotests.morda.pages.MordaType;
import ru.yandex.autotests.morda.rules.allure.AllureFeatureRule;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.rules.proxy.configactions.UserAgentAction;

import javax.ws.rs.core.UriBuilder;
import java.net.URI;

import static org.openqa.selenium.remote.DesiredCapabilities.firefox;
import static ru.yandex.autotests.morda.steps.NavigationSteps.open;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 27/02/15
 */
public class PdaRuMorda extends Morda<PdaRuPage> {
    private String userAgent;

    public PdaRuMorda(String scheme, MordaEnvironment environment, String userAgent) {
        super(scheme, environment);
        this.userAgent = userAgent;
    }

    public static PdaRuMorda pdaRu(String scheme, String environment, String userAgent) {
        return new PdaRuMorda(scheme,
                new MordaEnvironment("www", environment, false),
                userAgent
        );
    }

    @Override
    public MordaType getMordaType() {
        return MordaType.P_RU;
    }

    @Override
    public MordaAllureBaseRule getRule() {
        return getRule(firefox());
    }

    @Override
    public MordaAllureBaseRule getRule(DesiredCapabilities caps) {
        return new MordaAllureBaseRule(caps)
                .withRule(new AllureFeatureRule(getFeature()))
                .replaceProxyAction(UserAgentAction.class, userAgent);
    }

    @Override
    public PdaRuPage getPage(WebDriver driver) {
        return new PdaRuPage(driver);
    }

    @Override
    public URI getUrl() {
        return UriBuilder.fromUri("scheme://{env}yandex.ru/")
                .scheme(scheme)
                .build(environment.parseEnvironment());
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
