package ru.yandex.autotests.mordatmplerr.big;

import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.mordatmplerr.Properties;
import ru.yandex.autotests.mordatmplerr.mordatypes.Browser;
import ru.yandex.autotests.mordatmplerr.mordatypes.Morda;
import ru.yandex.autotests.mordatmplerr.steps.PassportSteps;
import ru.yandex.autotests.utils.morda.ParametrizationConverter;
import ru.yandex.qatools.allure.annotations.Features;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import static ru.yandex.autotests.mordacommonsteps.matchers.DocumentLoadedMatcher.contentLoaded;
import static ru.yandex.autotests.mordatmplerr.mordatypes.BetaMorda.betaMorda;
import static ru.yandex.autotests.mordatmplerr.mordatypes.ComTrMorda.comTrMorda;
import static ru.yandex.autotests.mordatmplerr.mordatypes.MainMorda.mainMorda;
import static ru.yandex.autotests.utils.morda.url.Domain.RU;
import static ru.yandex.qatools.htmlelements.matchers.MatcherDecorators.should;
import static ru.yandex.qatools.htmlelements.matchers.MatcherDecorators.timeoutHasExpired;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 19.03.14
 */

@Aqua.Test(title = "All")
@Features({"Big", "All"})
@RunWith(Parameterized.class)
public class AllBigTest {
    private static final Properties CONFIG = new Properties();
    private final String urlBig;
    private final String urlAll;

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule;
    private WebDriver driver;
    private CommonMordaSteps user;
    private PassportSteps userPassport;

    @Parameterized.Parameters(name = "{0}, {1}")
    public static Collection<Object[]> data() {
        List<Morda> data = new ArrayList<>();
        for (Browser browser : Browser.values()) {
            data.add(mainMorda(RU).withBrowser(browser));
            data.add(betaMorda(RU).withBrowser(browser));
            data.add(comTrMorda().withBrowser(browser));
        }
        return ParametrizationConverter.convert(data);
    }

    private Morda morda;

    public AllBigTest(Morda morda) {
        this.morda = morda;
        this.mordaAllureBaseRule = this.morda.getRule();
        this.driver = mordaAllureBaseRule.getDriver();
        this.user = new CommonMordaSteps(driver);
        this.userPassport = new PassportSteps(driver, mordaAllureBaseRule);
        urlBig = morda.getUrl(CONFIG.getMordaEnv().getEnv());
        urlAll = urlBig + "all";
    }

    @Test
    public void openAllPageBig() {
        user.opensPage(urlAll);
        should(contentLoaded()).whileWaitingUntil(timeoutHasExpired()).matches(driver);
    }

    @Test
    public void openAllPageBigLogin() {
        user.opensPage(urlBig);
        userPassport.login(morda, urlBig);
        user.opensPage(urlAll);
        should(contentLoaded()).whileWaitingUntil(timeoutHasExpired()).matches(driver);
    }
}
