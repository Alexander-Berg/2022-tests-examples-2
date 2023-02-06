package ru.yandex.autotests.mordacommonsteps.rules;

import org.junit.rules.TestWatcher;
import org.junit.runner.Description;
import org.openqa.selenium.OutputType;
import org.openqa.selenium.Platform;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.remote.DesiredCapabilities;

import ru.yandex.autotests.mordacommonsteps.Properties;
import ru.yandex.qatools.allure.annotations.Attachment;
import ru.yandex.qatools.selenium.grid.GridClient;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 29.10.13
 */
public class WebDriverRule extends TestWatcher {
    private static final Properties CONFIG = new Properties();

    private DesiredCapabilities caps;
    private WebDriverProxy webDriverProxy;
    private boolean screenShotOnFail;

    public WebDriverRule() {
        this(new DesiredCapabilities(
                CONFIG.getBrowserName(),
                CONFIG.getBrowserVersion(),
                Platform.ANY));
    }

    @Deprecated
    public WebDriverRule(WebDriver driver) {
    }

    public WebDriverRule(DesiredCapabilities caps) {
        this(new WebDriverProxy(), caps);
    }

    public WebDriverRule(DesiredCapabilities caps, boolean screenShotOnFail) {
        this(new WebDriverProxy(), caps, screenShotOnFail);
    }

    WebDriverRule(WebDriverProxy webDriverProxy, DesiredCapabilities caps) {
        this(webDriverProxy, caps, true);
    }

    WebDriverRule(WebDriverProxy webDriverProxy, DesiredCapabilities caps, boolean screenShotOnFail) {
        this.webDriverProxy = webDriverProxy;
        this.caps = caps;
        this.screenShotOnFail = screenShotOnFail;
    }

    @Override
    protected void starting(Description description) {
        webDriverProxy.setDriver(new GridClient().find(caps));
    }

    @Override
    protected void failed(Throwable e, Description description) {
        if (screenShotOnFail) {
            try {
                screenshot();
            } catch (Exception ignore) {
                ignore.printStackTrace();
            }
        }
    }

    @Override
    protected void finished(Description description) {
        try {
            webDriverProxy.close();
            webDriverProxy.quit();
        } catch (Exception ignore) {
            ignore.printStackTrace();
        }
    }

    public DesiredCapabilities getCaps() {
        return caps;
    }

    public WebDriver getDriver() {
        return webDriverProxy;
    }

    @Attachment
    private byte[] screenshot() {
        return webDriverProxy.getScreenshotAs(OutputType.BYTES);
    }

}
