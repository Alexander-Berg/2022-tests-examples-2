package ru.yandex.autotests.morda.pages.desktop.comtrfootball;

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
public class DesktopComTrFootballMorda extends Morda<DesktopComTrFootballPage> {
    private String club;

    private DesktopComTrFootballMorda(String scheme, MordaEnvironment environment, String club) {
        super(scheme, environment);
        this.club = club;
    }

    public static DesktopComTrFootballMorda desktopComTrBjk(String scheme, String environment) {
        return new DesktopComTrFootballMorda(scheme,
                new MordaEnvironment("www", environment, false),
                "bjk"
        );
    }

    public static DesktopComTrFootballMorda desktopComTrGs(String scheme, String environment) {
        return new DesktopComTrFootballMorda(scheme,
                new MordaEnvironment("www", environment, false),
                "gs"
        );
    }

    public static DesktopComTrFootballMorda desktopFamilyComTrBjk(String scheme, String environment) {
        return new DesktopComTrFootballMorda(scheme,
                new MordaEnvironment("aile", environment, false),
                "bjk"
        );
    }

    public static DesktopComTrFootballMorda desktopFamilyComTrGs(String scheme, String environment) {
        return new DesktopComTrFootballMorda(scheme,
                new MordaEnvironment("aile", environment, false),
                "gs"
        );
    }

    @Override
    public void initialize(WebDriver driver) {
        NavigationSteps.open(driver, getUrl());
    }

    @Override
    public MordaType getMordaType() {
        return MordaType.D_COMTRFOOTBALL;
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
    public DesktopComTrFootballPage getPage(WebDriver driver) {
        return new DesktopComTrFootballPage(driver);
    }

    @Override
    public URI getUrl() {
        return UriBuilder.fromUri("scheme://{env}yandex.com.tr/{club}")
                .scheme(scheme)
                .build(environment.parseEnvironment(), club);
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
        return UriBuilder.fromUri("https://www.yandex.com.tr/yandsearch").build();
    }

    @Override
    public String getCookieDomain() {
        return ".yandex.com.tr";
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
