package ru.yandex.autotests.morda.pages.touch.comtrwp;

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
public class TouchComTrWpMorda extends Morda<TouchComTrWpPage> {
    private String userAgent;

    public TouchComTrWpMorda(String scheme, MordaEnvironment environment, Region region, String userAgent) {
        super(scheme, environment);
        setRegion(region);
        setLanguage(Language.TR);
        this.userAgent = userAgent;
    }

    public static TouchComTrWpMorda touchComTrWp(String scheme, String environment, Region region, String userAgent) {
        return new TouchComTrWpMorda(scheme,
                new MordaEnvironment("www", environment, false),
                region,
                userAgent
        );
    }

    @Override
    public MordaType getMordaType() {
        return MordaType.T_COMTRWP;
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
    public TouchComTrWpPage getPage(WebDriver driver) {
        return new TouchComTrWpPage(driver);
    }

    @Override
    public URI getUrl() {
        return UriBuilder.fromUri("scheme://{env}yandex.com.tr/?q=")
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
//        TuneSteps.setRegion(driver, this.getTuneUrl(), this.getCookieDomain(), region);
        TuneSteps.setRegionWithCookie(driver, getCookieDomain(), region);
    }

    @Override
    public String getFeature() {
        return "touch wp " + getUrl();
    }

    @Override
    public String toString() {
        return "touch " + getUrl() + ", " + getRegion();
    }
}
