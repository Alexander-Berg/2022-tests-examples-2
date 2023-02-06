package ru.yandex.autotests.mordabackend.browser;

import org.junit.Test;
import org.junit.runner.RunWith;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mordabackend.MordaClient;
import ru.yandex.autotests.mordabackend.beans.browserdesc.BrowserDesc;
import ru.yandex.autotests.mordabackend.beans.cleanvars.Cleanvars;
import ru.yandex.autotests.mordabackend.useragents.UserAgent;
import ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils;
import ru.yandex.autotests.mordabackend.utils.runner.CleanvarsParametrizedRunner;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.autotests.utils.morda.url.Domain;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import javax.ws.rs.client.Client;

import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.on;
import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.autotests.mordabackend.blocks.CleanvarsBlock.BROWSERDESC;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.shouldHaveParameter;
import static ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils.parameters;

/**
 * User: ivannik
 * Date: 08.07.2014
 */
@Aqua.Test(title = "Browser Description")
@Features("Browser")
@Stories("Browser Description")
@RunWith(CleanvarsParametrizedRunner.class)
public class BrowserDescTest {

    @CleanvarsParametrizedRunner.Parameters("{4}")
    public static ParametersUtils parameters =
            parameters(Domain.RU)
                    .withUserAgents(UserAgent.values())
                    .withCleanvarsBlocks(BROWSERDESC);


    private UserAgent userAgent;
    private Cleanvars cleanvars;

    public BrowserDescTest(MordaClient mordaClient, Client client, Cleanvars cleanvars,
                           Region region, UserAgent userAgent) {
        this.userAgent = userAgent;
        this.cleanvars = cleanvars;
    }

    @Test
    public void operatingSystem() {
        shouldHaveParameter(cleanvars.getBrowserDesc(), having(on(BrowserDesc.class).getOSFamily(),
                equalTo(userAgent.getOSFamily())));
        shouldHaveParameter(cleanvars.getBrowserDesc(), having(on(BrowserDesc.class).getOSName(),
                equalTo(userAgent.getOSName())));
        shouldHaveParameter(cleanvars.getBrowserDesc(), having(on(BrowserDesc.class).getOSVersion(),
                equalTo(userAgent.getOSVersion())));
    }

    @Test
    public void browserBase() {
        shouldHaveParameter(cleanvars.getBrowserDesc(), having(on(BrowserDesc.class).getBrowserBase(),
                equalTo(userAgent.getBrowserBase())));
        shouldHaveParameter(cleanvars.getBrowserDesc(), having(on(BrowserDesc.class).getBrowserBaseVersion(),
                equalTo(userAgent.getBrowserBaseVersion())));
    }

    @Test
    public void browserEngine() {
        shouldHaveParameter(cleanvars.getBrowserDesc(), having(on(BrowserDesc.class).getBrowserEngine(),
                equalTo(userAgent.getBrowserEngine())));
        shouldHaveParameter(cleanvars.getBrowserDesc(), having(on(BrowserDesc.class).getBrowserEngineVersion(),
                equalTo(userAgent.getBrowserEngineVersion())));
    }

    @Test
    public void browserName() {
        shouldHaveParameter(cleanvars.getBrowserDesc(), having(on(BrowserDesc.class).getBrowserName(),
                equalTo(userAgent.getBrowserName())));
        shouldHaveParameter(cleanvars.getBrowserDesc(), having(on(BrowserDesc.class).getBrowserVersion(),
                equalTo(userAgent.getBrowserVersion())));
    }

    @Test
    public void historySupportFlag() {
        shouldHaveParameter(cleanvars.getBrowserDesc(), having(on(BrowserDesc.class).getHistorySupport(),
                equalTo(userAgent.getHistorySupport())));
    }

    @Test
    public void isBrowserFlag() {
        shouldHaveParameter(cleanvars.getBrowserDesc(), having(on(BrowserDesc.class).getIsBrowser(),
                equalTo(userAgent.getIsBrowser())));
    }

    @Test
    public void isMobileFlag() {
        shouldHaveParameter(cleanvars.getBrowserDesc(), having(on(BrowserDesc.class).getIsMobile(),
                equalTo(userAgent.getIsMobile())));
    }

    @Test
    public void isTabletFlag() {
        shouldHaveParameter(cleanvars.getBrowserDesc(), having(on(BrowserDesc.class).getIsTablet(),
                equalTo(userAgent.getIsTablet())));
    }

    @Test
    public void isTouchFlag() {
        shouldHaveParameter(cleanvars.getBrowserDesc(), having(on(BrowserDesc.class).getIsTouch(),
                equalTo(userAgent.getIsTouch())));
    }

    @Test
    public void localStorageSupportFlag() {
        shouldHaveParameter(cleanvars.getBrowserDesc(), having(on(BrowserDesc.class).getLocalStorageSupport(),
                equalTo(userAgent.getLocalStorageSupport())));
    }

    @Test
    public void postMessageSupportFlag() {
        shouldHaveParameter(cleanvars.getBrowserDesc(), having(on(BrowserDesc.class).getPostMessageSupport(),
                equalTo(userAgent.getPostMessageSupport())));
    }

    @Test
    public void x64Flag() {
        shouldHaveParameter(cleanvars.getBrowserDesc(), having(on(BrowserDesc.class).getX64(),
                equalTo(userAgent.getX64())));
    }

    @Test
    public void multiTouchFlag() {
        shouldHaveParameter(cleanvars.getBrowserDesc(), having(on(BrowserDesc.class).getMultiTouch(),
                equalTo(userAgent.getMultiTouch())));
    }

    @Test
    public void inAppBrowserFlag() {
        shouldHaveParameter(cleanvars.getBrowserDesc(), having(on(BrowserDesc.class).getInAppBrowser(),
                equalTo(userAgent.getInAppBrowser())));
    }
}
