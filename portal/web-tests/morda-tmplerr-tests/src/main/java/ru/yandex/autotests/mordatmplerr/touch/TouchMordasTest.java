package ru.yandex.autotests.mordatmplerr.touch;

import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.mordatmplerr.Properties;
import ru.yandex.autotests.mordatmplerr.mordatypes.Morda;
import ru.yandex.autotests.mordatmplerr.mordatypes.TouchType;
import ru.yandex.autotests.mordatmplerr.steps.PassportSteps;
import ru.yandex.autotests.utils.morda.ParametrizationConverter;
import ru.yandex.qatools.allure.annotations.Features;

import java.net.MalformedURLException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collection;
import java.util.List;

import static ru.yandex.autotests.mordacommonsteps.matchers.DocumentLoadedMatcher.contentLoaded;
import static ru.yandex.autotests.mordatmplerr.mordatypes.BetaMorda.betaMorda;
import static ru.yandex.autotests.mordatmplerr.mordatypes.Browser.CHROME;
import static ru.yandex.autotests.mordatmplerr.mordatypes.ComMorda.comMorda;
import static ru.yandex.autotests.mordatmplerr.mordatypes.ComTrMorda.comTrMorda;
import static ru.yandex.autotests.mordatmplerr.mordatypes.MainMorda.mainMorda;
import static ru.yandex.autotests.mordatmplerr.mordatypes.TouchType.ANDROID_CHROME;
import static ru.yandex.autotests.mordatmplerr.mordatypes.TouchType.IPHONE_SAFARI;
import static ru.yandex.autotests.mordatmplerr.mordatypes.TouchType.SHELL;
import static ru.yandex.autotests.mordatmplerr.mordatypes.TouchType.TIZEN;
import static ru.yandex.autotests.mordatmplerr.mordatypes.TouchType.WP;
import static ru.yandex.autotests.mordatmplerr.mordatypes.YaRuMorda.yaruMorda;
import static ru.yandex.autotests.utils.morda.url.Domain.RU;
import static ru.yandex.qatools.htmlelements.matchers.MatcherDecorators.should;
import static ru.yandex.qatools.htmlelements.matchers.MatcherDecorators.timeoutHasExpired;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 08.04.14
 */

@Aqua.Test(title = "Open Mordas")
@Features({"Touch", "Open Mordas"})
@RunWith(Parameterized.class)
public class TouchMordasTest {

    private static final Properties CONFIG = new Properties();
    private final String url;

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule;
    private WebDriver driver;
    private CommonMordaSteps user;
    private PassportSteps userPassport;

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> data() {
        List<Morda> data = new ArrayList<>();
        data.add(yaruMorda().withTouchType(SHELL)
                .withBrowser(CHROME)
                .withParameter("shell", "1")
                .withParameter("clid", "1864803"));
        for (TouchType touchType : Arrays.asList(IPHONE_SAFARI, ANDROID_CHROME, TIZEN, WP)) {
            data.add(mainMorda(RU).withTouchType(touchType).withBrowser(CHROME));
            data.add(betaMorda(RU).withTouchType(touchType).withBrowser(CHROME));
            data.add(comTrMorda().withTouchType(touchType).withBrowser(CHROME));
            data.add(comMorda().withTouchType(touchType).withBrowser(CHROME));
            data.add(yaruMorda().withTouchType(touchType).withBrowser(CHROME));
        }
        return ParametrizationConverter.convert(data);
    }

    private Morda morda;

    public TouchMordasTest(Morda morda) {
        this.morda = morda;
        this.mordaAllureBaseRule = this.morda.getRule();
        this.driver = mordaAllureBaseRule.getDriver();
        this.user = new CommonMordaSteps(driver);
        this.userPassport = new PassportSteps(driver, mordaAllureBaseRule);
        url = morda.getUrl(CONFIG.getMordaEnv().getEnv());
    }

    @Test
    public void openPageTouch() {
        user.opensPage(url);
        should(contentLoaded()).whileWaitingUntil(timeoutHasExpired()).matches(driver);
    }

    @Test
    public void openPageTouchLogin() throws MalformedURLException {
        user.opensPage(url);
        userPassport.login(morda, url);
        user.opensPage(url);
        should(contentLoaded()).whileWaitingUntil(timeoutHasExpired()).matches(driver);
    }

}
