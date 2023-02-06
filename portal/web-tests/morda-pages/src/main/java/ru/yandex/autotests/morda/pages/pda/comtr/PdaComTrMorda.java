package ru.yandex.autotests.morda.pages.pda.comtr;

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
public class PdaComTrMorda extends Morda<PdaComTrPage> {
    private String userAgent;

    public PdaComTrMorda(String scheme, MordaEnvironment environment, String userAgent) {
        super(scheme, environment);
        this.userAgent = userAgent;
    }

    public static PdaComTrMorda pdaComTr(String scheme, String environment, String userAgent) {
        return new PdaComTrMorda(scheme,
                new MordaEnvironment("www", environment, false),
                userAgent
        );
    }

    @Override
    public MordaType getMordaType() {
        return MordaType.P_COMTR;
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
    public PdaComTrPage getPage(WebDriver driver) {
        return new PdaComTrPage(driver);
    }

    @Override
    public URI getUrl() {
        return UriBuilder.fromUri("scheme://{env}yandex.com.tr/")
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
        return UriBuilder.fromUri("{scheme}://www.yandex.com.tr/msearch")
                .build(scheme);
    }

    @Override
    public void initialize(WebDriver driver) {
        open(driver, getUrl());
    }

    @Override
    public String getCookieDomain() {
        return ".yandex.com.tr";
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
