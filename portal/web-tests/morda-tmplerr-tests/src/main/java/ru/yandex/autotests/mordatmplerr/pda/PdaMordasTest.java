package ru.yandex.autotests.mordatmplerr.pda;

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
import ru.yandex.autotests.mordatmplerr.steps.PassportSteps;
import ru.yandex.autotests.utils.morda.ParametrizationConverter;
import ru.yandex.qatools.allure.annotations.Features;

import java.net.MalformedURLException;
import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import static ru.yandex.autotests.mordacommonsteps.matchers.DocumentLoadedMatcher.contentLoaded;
import static ru.yandex.autotests.mordatmplerr.mordatypes.Browser.CHROME;
import static ru.yandex.autotests.mordatmplerr.mordatypes.ComMorda.comMorda;
import static ru.yandex.autotests.mordatmplerr.mordatypes.ComTrMorda.comTrMorda;
import static ru.yandex.autotests.mordatmplerr.mordatypes.MainMorda.mainMorda;
import static ru.yandex.autotests.mordatmplerr.mordatypes.TouchType.PDA;
import static ru.yandex.autotests.mordatmplerr.mordatypes.YaRuMorda.yaruMorda;
import static ru.yandex.autotests.utils.morda.url.Domain.RU;
import static ru.yandex.qatools.htmlelements.matchers.MatcherDecorators.should;
import static ru.yandex.qatools.htmlelements.matchers.MatcherDecorators.timeoutHasExpired;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 08.04.14
 */

@Aqua.Test(title = "Open Mordas")
@Features({"PDA", "Open Mordas"})
@RunWith(Parameterized.class)
public class PdaMordasTest {

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
        data.add(mainMorda(RU).withTouchType(PDA).withBrowser(CHROME));
        data.add(comTrMorda().withTouchType(PDA).withBrowser(CHROME));
        data.add(comMorda().withTouchType(PDA).withBrowser(CHROME));
        data.add(yaruMorda().withTouchType(PDA).withBrowser(CHROME));
        return ParametrizationConverter.convert(data);
    }

    private Morda morda;

    public PdaMordasTest(Morda morda) {
        this.morda = morda;
        this.mordaAllureBaseRule = this.morda.getRule();
        this.driver = mordaAllureBaseRule.getDriver();
        this.user = new CommonMordaSteps(driver);
        this.userPassport = new PassportSteps(driver, mordaAllureBaseRule);
        url = morda.getUrl(CONFIG.getMordaEnv().getEnv());
    }

    @Test
    public void openPagePda() {
        user.opensPage(url);
        should(contentLoaded()).whileWaitingUntil(timeoutHasExpired()).matches(driver);
    }

    @Test
    public void openPagePdaLogin() throws MalformedURLException {
        user.opensPage(url);
        userPassport.login(morda, url);
        System.out.println(driver.manage().getCookies());
        user.opensPage(url);
        should(contentLoaded()).whileWaitingUntil(timeoutHasExpired()).matches(driver);
    }

}
