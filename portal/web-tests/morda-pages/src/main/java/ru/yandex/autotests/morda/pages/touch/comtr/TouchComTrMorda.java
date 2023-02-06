package ru.yandex.autotests.morda.pages.touch.comtr;

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
import ru.yandex.autotests.mordacommonsteps.rules.proxy.configactions.UserAgentAction;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.autotests.utils.morda.region.Region;

import javax.ws.rs.core.UriBuilder;
import java.net.URI;
import java.util.HashSet;
import java.util.List;

import static java.util.Arrays.asList;
import static org.openqa.selenium.remote.DesiredCapabilities.firefox;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 27/02/15
 */
public class TouchComTrMorda extends Morda<TouchComTrPage> {
    private String userAgent;

    public TouchComTrMorda(String scheme, MordaEnvironment environment, Region region, String userAgent) {
        super(scheme, environment);
        setRegion(region);
        setLanguage(Language.TR);
        this.userAgent = userAgent;
    }

    public static TouchComTrMorda touchComTr(String scheme, String environment, Region region, String userAgent) {
        return new TouchComTrMorda(scheme,
                new MordaEnvironment("www", environment, false),
                region,
                userAgent
        );
    }

    @Override
    public MordaType getMordaType() {
        return MordaType.T_COMTR;
    }

    @Override
    public MordaAllureBaseRule getRule() {
        return getRule(firefox());
    }

    @Override
    public MordaAllureBaseRule getRule(DesiredCapabilities caps) {
        List<Header> headers = asList(
                new Header("X-Yandex-TestCounters", "0")
        );

        return new MordaAllureBaseRule(caps)
                .withRule(new AllureFeatureRule(getFeature()))
                .replaceProxyAction(UserAgentAction.class, userAgent)
                .mergeProxyAction(HeaderAction.class, new HashSet<>(headers));
    }

    @Override
    public String getCookieDomain() {
        return ".yandex.com.tr";
    }

    @Override
    public TouchComTrPage getPage(WebDriver driver) {
        return new TouchComTrPage(driver);
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
        return UriBuilder.fromUri("{scheme}://www.yandex.com.tr/search/touch/")
                .build(scheme);
    }

    @Override
    public void initialize(WebDriver driver) {
        NavigationSteps.open(driver, getUrl());
//        TuneSteps.setRegionNewTune(driver, getUrl(), this.getCookieDomain(), region);
        TuneSteps.setRegionWithCookie(driver, getCookieDomain(), region);
    }

    @Override
    public String getFeature() {
        return "touch " + getUrl();
    }

    @Override
    public String toString() {
        return "touch " + getUrl() + ", " + getRegion();
    }
}
