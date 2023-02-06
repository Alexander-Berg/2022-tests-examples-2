package ru.yandex.autotests.morda.pages.pda.com;

import org.openqa.selenium.WebDriver;
import org.openqa.selenium.remote.DesiredCapabilities;
import ru.yandex.autotests.morda.pages.Morda;
import ru.yandex.autotests.morda.pages.MordaType;
import ru.yandex.autotests.morda.rules.allure.AllureFeatureRule;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.rules.proxy.configactions.Header;
import ru.yandex.autotests.mordacommonsteps.rules.proxy.configactions.HeaderAction;
import ru.yandex.autotests.mordacommonsteps.rules.proxy.configactions.UserAgentAction;

import javax.ws.rs.core.UriBuilder;
import java.net.URI;
import java.util.HashSet;
import java.util.List;

import static java.util.Arrays.asList;
import static org.openqa.selenium.remote.DesiredCapabilities.firefox;
import static ru.yandex.autotests.morda.steps.NavigationSteps.open;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 27/02/15
 */
public class PdaComMorda extends Morda<PdaComPage> {
    private String userAgent;

    public PdaComMorda(String scheme, MordaEnvironment environment, String userAgent) {
        super(scheme, environment);
        this.userAgent = userAgent;
    }

    public static PdaComMorda pdaCom(String scheme, String environment, String userAgent) {
        return new PdaComMorda(scheme,
                new MordaEnvironment("www", environment, false),
                userAgent
        );
    }

    @Override
    public MordaType getMordaType() {
        return MordaType.P_COM;
    }

    @Override
    public MordaAllureBaseRule getRule() {
        return getRule(firefox());
    }

    @Override
    public MordaAllureBaseRule getRule(DesiredCapabilities caps) {
        final String BOSTON_IP = "158.121.51.122";
        List<Header> headers = asList(
                new Header("X-Forwarded-For", BOSTON_IP),
                new Header("No-Redirect", "1")
        );
        return new MordaAllureBaseRule(caps)
                .replaceProxyAction(UserAgentAction.class, userAgent)
                .withRule(new AllureFeatureRule(getFeature()))
                .mergeProxyAction(HeaderAction.class, new HashSet<>(headers));
    }

    @Override
    public PdaComPage getPage(WebDriver driver) {
        return new PdaComPage(driver);
    }

    @Override
    public URI getUrl() {
        return UriBuilder.fromUri("scheme://{env}yandex.com/")
                .scheme(scheme)
                .build(environment.parseEnvironment());
    }

    @Override
    public URI getPassportUrl(String passportEnv) {
        return UriBuilder.fromUri("https://{passportEnv}.yandex.com/")
                .build(passportEnv);
    }

    @Override
    public URI getTuneUrl(String tuneEnv) {
        return UriBuilder.fromUri("https://{tuneEnv}.yandex.com/")
                .build(tuneEnv);
    }

    @Override
    public void initialize(WebDriver driver) {
        open(driver, getUrl());
    }

    @Override
    public URI getSerpUrl() {
        return UriBuilder.fromUri("https://www.yandex.com/yandsearch").build();
    }

    @Override
    public String getCookieDomain() {
        return ".yandex.com";
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
