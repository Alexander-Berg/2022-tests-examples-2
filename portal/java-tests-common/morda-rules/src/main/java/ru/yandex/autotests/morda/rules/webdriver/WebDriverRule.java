package ru.yandex.autotests.morda.rules.webdriver;

import org.apache.log4j.Logger;
import org.junit.rules.TestWatcher;
import org.junit.runner.Description;
import org.openqa.selenium.OutputType;
import org.openqa.selenium.Platform;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.remote.DesiredCapabilities;
import ru.yandex.autotests.morda.rules.MordaRulesProperties;
import ru.yandex.qatools.allure.annotations.Attachment;
import ru.yandex.qatools.selenium.grid.GridClient;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 29.10.13
 */
public class WebDriverRule extends TestWatcher {
    private static final MordaRulesProperties CONFIG = new MordaRulesProperties();
    private static final Logger LOG = Logger.getLogger(WebDriverRule.class);

    private DesiredCapabilities caps;
    private WebDriverProxy webDriverProxy;
    private boolean screenshotOnFail;

    public WebDriverRule() {
        this(new DesiredCapabilities(CONFIG.getBrowserName(), CONFIG.getBrowserVersion(), Platform.ANY));
    }

    public WebDriverRule(DesiredCapabilities caps) {
        this(new WebDriverProxy(), caps);
    }

    WebDriverRule(WebDriverProxy webDriverProxy, DesiredCapabilities caps) {
        this.webDriverProxy = webDriverProxy;
        this.caps = caps;
        this.screenshotOnFail = true;
    }

    public WebDriverRule withScreenshotOnFail(boolean screenshotOnFail) {
        this.screenshotOnFail = screenshotOnFail;
        return this;
    }

    @Override
    protected void starting(Description description) {
        LOG.info("Obtaining " + caps.getBrowserName());
        webDriverProxy.setDriver(new GridClient().find(caps));
        LOG.info("Obtained " + caps.getBrowserName());
    }

    @Override
    protected void failed(Throwable e, Description description) {
        if (screenshotOnFail) {
            LOG.info("Taking screenshot");
            try {
                screenshot();
            } catch (Exception e2) {
                LOG.warn("Failed to take screenshot", e2);
            }
        }
    }

    @Override
    protected void finished(Description description) {
        LOG.info("Closing " + caps.getBrowserName());
        try {
            webDriverProxy.close();
            webDriverProxy.quit();
            LOG.info("Closed " + caps.getBrowserName());
        } catch (Exception e) {
            LOG.warn("Failed to close the driver", e);
        }
    }

    public DesiredCapabilities getCaps() {
        return caps;
    }

    public WebDriver getDriver() {
        return webDriverProxy;
    }

    public boolean isScreenshotOnFail() {
        return screenshotOnFail;
    }

    @Attachment
    private byte[] screenshot() {
        return webDriverProxy.getScreenshotAs(OutputType.BYTES);
    }

}
