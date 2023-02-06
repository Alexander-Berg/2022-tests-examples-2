package ru.yandex.autotests.morda.pages.desktop.hwlgV2;

import org.openqa.selenium.JavascriptExecutor;
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
 * User: asamar
 * Date: 30.10.2015.
 */
public class DesktopHwLgV2Morda extends Morda<DesktopHwLgV2Page> {

    private DesktopHwLgV2Morda(String scheme, MordaEnvironment environment) {
        super(scheme, environment);
    }

    public static DesktopHwLgV2Morda desktopHwLgV2(String scheme, String environment) {
        return new DesktopHwLgV2Morda(scheme,
                new MordaEnvironment("hw", environment, false)
        );
    }

    @Override
    public MordaType getMordaType() {
        return MordaType.D_HWLG;
    }

    @Override
    public void initialize(WebDriver driver){
        NavigationSteps.open(driver, getUrl());
        ((JavascriptExecutor)driver).executeScript("localStorage.setItem(\"geoId\", '{\"obj\": 2}')", 2);
        driver.navigate().refresh();
    }

    @Override
    public MordaAllureBaseRule getRule(){
        return getRule(firefox());
    }

    @Override
    public MordaAllureBaseRule getRule(DesiredCapabilities caps) {
        return new MordaAllureBaseRule(caps)
                .withRule(new AllureFeatureRule(getFeature()));
    }

    @Override
    public DesktopHwLgV2Page getPage(WebDriver driver) {
        return new DesktopHwLgV2Page(driver);
    }

    @Override
    public URI getUrl() {
        return UriBuilder.fromUri("{scheme}://{env}yandex.ru/lg-v2/")
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
        return UriBuilder.fromUri("{scheme}://yandex.ru/yandsearch")
                .build(scheme);
    }

    @Override
    public String getCookieDomain() {
        return ".yandex.ru";
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
