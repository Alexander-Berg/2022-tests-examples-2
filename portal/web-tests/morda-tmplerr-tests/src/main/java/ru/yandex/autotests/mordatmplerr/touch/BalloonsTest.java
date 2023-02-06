package ru.yandex.autotests.mordatmplerr.touch;

import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.rules.proxy.configactions.CookieAction;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.mordatmplerr.Properties;
import ru.yandex.autotests.mordatmplerr.mordatypes.Browser;
import ru.yandex.autotests.mordatmplerr.mordatypes.Morda;
import ru.yandex.autotests.mordatmplerr.mordatypes.TouchType;
import ru.yandex.autotests.utils.morda.ParametrizationConverter;
import ru.yandex.autotests.utils.morda.cookie.Cookie;
import ru.yandex.autotests.utils.morda.cookie.CookieManager;
import ru.yandex.qatools.allure.annotations.Features;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collection;
import java.util.HashSet;
import java.util.List;
import java.util.concurrent.TimeUnit;

import static ru.yandex.autotests.mordacommonsteps.matchers.DocumentLoadedMatcher.contentLoaded;
import static ru.yandex.autotests.mordatmplerr.mordatypes.ComTrMorda.comTrMorda;
import static ru.yandex.autotests.mordatmplerr.mordatypes.MainMorda.mainMorda;
import static ru.yandex.autotests.utils.morda.url.Domain.RU;
import static ru.yandex.qatools.htmlelements.matchers.MatcherDecorators.should;
import static ru.yandex.qatools.htmlelements.matchers.MatcherDecorators.timeoutHasExpired;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 19.03.14
 */

@Aqua.Test(title = "Balloons")
@Features({"Touch", "Balloons"})
@RunWith(Parameterized.class)
public class BalloonsTest {
    private static final Properties CONFIG = new Properties();
    private static final long OLD_TIMESTAMP = (System.currentTimeMillis() - TimeUnit.DAYS.toMillis(5)) / 1000;
    private final String url;

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule;

    private WebDriver driver;
    private CommonMordaSteps user;

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> data() {
        List<Morda> data = new ArrayList<>();
        data.add(mainMorda(RU).withTouchType(TouchType.IPHONE_SAFARI).withBrowser(Browser.CHROME));
        data.add(mainMorda(RU).withTouchType(TouchType.IPHONE_CHROME).withBrowser(Browser.CHROME));
        data.add(mainMorda(RU).withTouchType(TouchType.TABLET).withBrowser(Browser.CHROME));
        data.add(comTrMorda().withTouchType(TouchType.IPHONE_SAFARI).withBrowser(Browser.CHROME));
        data.add(comTrMorda().withTouchType(TouchType.IPHONE_CHROME).withBrowser(Browser.CHROME));
        data.add(comTrMorda().withTouchType(TouchType.TABLET).withBrowser(Browser.CHROME));
        return ParametrizationConverter.convert(data);
    }

    private Morda morda;

    public BalloonsTest(Morda morda) {
        this.morda = morda;
        this.mordaAllureBaseRule = this.morda.getRule()
                .mergeProxyAction(CookieAction.class, new HashSet<>(Arrays.asList(
                        new ru.yandex.autotests.mordacommonsteps.rules.proxy.configactions.Cookie(
                                Cookie.YANDEXUID.getName(), "16435416" + OLD_TIMESTAMP))));
        this.driver = mordaAllureBaseRule.getDriver();
        this.user = new CommonMordaSteps(driver);
        url = morda.getUrl(CONFIG.getMordaEnv().getEnv());
    }

    @Test
    public void oldCookieTouch() throws InterruptedException {
        user.opensPage(url);
        user.opensPage(url);
        should(contentLoaded()).whileWaitingUntil(timeoutHasExpired()).matches(driver);
    }

    @Test
    public void wrongDateTouch() throws InterruptedException {
        user.opensPage(url + "?date=2014-01-01");
        user.opensPage(url + "?date=2014-01-01");
        should(contentLoaded()).whileWaitingUntil(timeoutHasExpired()).matches(driver);
    }

    @Test
    public void oldCookieBig() throws InterruptedException {
        user.opensPage(url);
        CookieManager.addCookie(driver, Cookie.MY, "YywBAQA=");
        user.opensPage(url);
        should(contentLoaded()).whileWaitingUntil(timeoutHasExpired()).matches(driver);
    }
}
