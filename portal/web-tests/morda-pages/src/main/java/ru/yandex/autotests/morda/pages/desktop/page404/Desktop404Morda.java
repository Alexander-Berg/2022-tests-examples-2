package ru.yandex.autotests.morda.pages.desktop.page404;

import org.openqa.selenium.WebDriver;
import org.openqa.selenium.remote.DesiredCapabilities;
import ru.yandex.autotests.morda.pages.Morda;
import ru.yandex.autotests.morda.pages.MordaType;
import ru.yandex.autotests.morda.rules.allure.AllureFeatureRule;
import ru.yandex.autotests.morda.steps.NavigationSteps;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;

import javax.ws.rs.core.UriBuilder;
import java.net.URI;

import static org.openqa.selenium.remote.DesiredCapabilities.firefox;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 27/02/15
 */
public class Desktop404Morda extends Morda<Desktop404Page> {
    private String tld;

    private Desktop404Morda(String scheme, MordaEnvironment environment, String tld) {
        super(scheme, environment);
        this.tld = tld;
    }

    public static Desktop404Morda desktop404ru(String scheme, String environment) {
        return new Desktop404Morda(scheme,
                new MordaEnvironment("www", environment, false),
                ".ru"
        );
    }

    public static Desktop404Morda desktop404ua(String scheme, String environment) {
        return new Desktop404Morda(scheme,
                new MordaEnvironment("www", environment, false),
                ".ua"
        );
    }

    public static Desktop404Morda desktop404by(String scheme, String environment) {
        return new Desktop404Morda(scheme,
                new MordaEnvironment("www", environment, false),
                ".by"
        );
    }

    public static Desktop404Morda desktop404kz(String scheme, String environment) {
        return new Desktop404Morda(scheme,
                new MordaEnvironment("www", environment, false),
                ".kz"
        );
    }

    public static Desktop404Morda desktop404com(String scheme, String environment) {
        return new Desktop404Morda(scheme,
                new MordaEnvironment("www", environment, false),
                ".com"
        );
    }

    public static Desktop404Morda desktop404comTr(String scheme, String environment) {
        return new Desktop404Morda(scheme,
                new MordaEnvironment("www", environment, false),
                ".com.tr"
        );
    }

    @Override
    public void initialize(WebDriver driver) {
        NavigationSteps.open(driver, getUrl());
    }

    @Override
    public MordaType getMordaType() {
        return MordaType.D_PAGE404;
    }

    @Override
    public MordaAllureBaseRule getRule() {
        return getRule(firefox());
    }

    @Override
    public MordaAllureBaseRule getRule(DesiredCapabilities caps) {
        return new MordaAllureBaseRule(caps)
                .withRule(new AllureFeatureRule(getFeature()));
    }

    @Override
    public Desktop404Page getPage(WebDriver driver) {
        return new Desktop404Page(driver);
    }

    @Override
    public URI getUrl() {
        return UriBuilder.fromUri("scheme://{env}yandex{tld}/sl/blah")
                .scheme(scheme)
                .build(environment.parseEnvironment(), tld);
    }

    @Override
    public URI getPassportUrl(String passportEnv) {

        return UriBuilder.fromUri("https://{passportEnv}.yandex{tld}/")
                .build(passportEnv, tld);
    }

    @Override
    public URI getTuneUrl(String tuneEnv) {
        return UriBuilder.fromUri("https://{tuneEnv}.yandex{tld}/")
                .build(tuneEnv, tld);
    }

    @Override
    public URI getSerpUrl() {
        return UriBuilder.fromUri("{scheme}://yandex{tld}/yandsearch")
                .build(scheme, tld);
    }

    @Override
    public String getCookieDomain() {
        return String.format(".yandex%s", tld);
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
