package ru.yandex.autotests.morda.pages.touch.comtrall;

import org.openqa.selenium.WebDriver;
import org.openqa.selenium.remote.DesiredCapabilities;
import ru.yandex.autotests.morda.pages.Morda;
import ru.yandex.autotests.morda.pages.MordaType;
import ru.yandex.autotests.morda.rules.allure.AllureFeatureRule;
import ru.yandex.autotests.morda.steps.NavigationSteps;
import ru.yandex.autotests.morda.steps.TuneSteps;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.rules.proxy.configactions.UserAgentAction;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.autotests.utils.morda.region.Region;

import javax.ws.rs.core.UriBuilder;
import java.net.URI;

import static org.openqa.selenium.remote.DesiredCapabilities.firefox;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 27/02/15
 */
public class TouchComTrAllMorda extends Morda<TouchComTrAllPage> {
    private String userAgent;

    public TouchComTrAllMorda(String scheme, MordaEnvironment environment, Region region, String userAgent) {
        super(scheme, environment);
        setRegion(region);
        setLanguage(Language.TR);
        this.userAgent = userAgent;
    }

    public static TouchComTrAllMorda touchComTrAll(String scheme, String environment, Region region, String userAgent) {
        return new TouchComTrAllMorda(scheme,
                new MordaEnvironment("www", environment, false),
                region,
                userAgent
        );
    }

    @Override
    public MordaType getMordaType() {
        return MordaType.T_COMTRALL;
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
    public String getCookieDomain() {
        return ".yandex.com.tr";
    }

    @Override
    public TouchComTrAllPage getPage(WebDriver driver) {
        return new TouchComTrAllPage(driver);
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
        return UriBuilder.fromUri("{scheme}://www.yandex.com.tr/touchsearch")
                .build(scheme);
    }

    @Override
    public void initialize(WebDriver driver) {
        NavigationSteps.open(driver, getUrl());
        TuneSteps.setRegion(driver, this.getTuneUrl(), this.getCookieDomain(), region);
//        TuneSteps.setRegionWithCookie(driver, getCookieDomain(), region);
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
