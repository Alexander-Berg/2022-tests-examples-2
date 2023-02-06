package ru.yandex.autotests.morda.rules.proxy;

import net.lightbody.bmp.BrowserMobProxy;
import net.lightbody.bmp.BrowserMobProxyServer;
import net.lightbody.bmp.client.ClientUtil;
import net.lightbody.bmp.proxy.CaptureType;
import org.apache.log4j.Logger;
import org.junit.rules.TestWatcher;
import org.junit.runner.Description;
import org.openqa.selenium.Proxy;
import org.openqa.selenium.remote.CapabilityType;
import org.openqa.selenium.remote.DesiredCapabilities;
import ru.yandex.autotests.morda.rules.proxy.actions.Action;

import java.util.ArrayList;
import java.util.List;

import static java.util.Arrays.asList;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 07.10.13
 */
public class MordaProxyRule extends TestWatcher {
    private static final Logger LOG = Logger.getLogger(MordaProxyRule.class);
    private final List<Action> proxyActions;

    private BrowserMobProxy proxyServer;
    private DesiredCapabilities caps;

    public MordaProxyRule(DesiredCapabilities caps) {
        this.proxyActions = new ArrayList<>();
        this.caps = caps;
    }

    @Override
    protected void starting(Description description) {
        try {
            LOG.info("Starting proxy server");
            proxyServer = new BrowserMobProxyServer();
            proxyServer.start();
            LOG.info("Started proxy server on port " + proxyServer.getPort());
            proxyServer.enableHarCaptureTypes(CaptureType.RESPONSE_HEADERS);
            proxyServer.enableHarCaptureTypes(CaptureType.REQUEST_HEADERS);
            prepareCapabilities();
        } catch (Exception e) {
            throw new RuntimeException("Failed to start proxy server. " + e.getMessage());
        }
        configure();
    }

    @Override
    protected void finished(Description description) {
        try {
            LOG.info("Stopping proxy server");
            proxyServer.stop();
            LOG.info("Stopped proxy server");
        } catch (Exception e) {
            throw new RuntimeException("Failed to stop proxy server. " + e.getMessage());
        }
    }

    public MordaProxyRule register(Action... actions) {
        proxyActions.addAll(asList(actions));
        return this;
    }

    public MordaProxyRule configure() {
        proxyActions.forEach(Action::perform);
        return this;
    }

    private void prepareCapabilities() {
        Proxy proxy = ClientUtil.createSeleniumProxy(proxyServer);
        LOG.info("Setup " + caps.getBrowserName() + " to use selenium proxy at " + proxy.getHttpProxy());
        if (caps.getBrowserName().contains("chrome")) {
            List<String> switches = (List<String>) caps.getCapability("chrome.switches");
            if (switches == null) {
                switches = new ArrayList<>();
            }
            switches.add("--proxy-server=" + proxy.getHttpProxy());
            caps.setCapability("chrome.switches", switches);
        }
        caps.setCapability(CapabilityType.PROXY, proxy);
    }

    public DesiredCapabilities getCapabilities() {
        return caps;
    }

    public BrowserMobProxy getProxyServer() {
        return proxyServer;
    }
}
