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
import ru.yandex.autotests.mordatmplerr.mordatypes.ComTrMorda;
import ru.yandex.autotests.mordatmplerr.mordatypes.Morda;
import ru.yandex.autotests.utils.morda.ParametrizationConverter;
import ru.yandex.autotests.utils.morda.cookie.CookieManager;
import ru.yandex.qatools.allure.annotations.Features;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import static org.junit.Assume.assumeFalse;
import static ru.yandex.autotests.mordacommonsteps.matchers.DocumentLoadedMatcher.contentLoaded;
import static ru.yandex.autotests.mordatmplerr.mordatypes.ComTrMorda.comTrMorda;
import static ru.yandex.autotests.mordatmplerr.mordatypes.MainMorda.mainMorda;
import static ru.yandex.autotests.utils.morda.url.Domain.RU;
import static ru.yandex.qatools.htmlelements.matchers.MatcherDecorators.should;
import static ru.yandex.qatools.htmlelements.matchers.MatcherDecorators.timeoutHasExpired;


@Aqua.Test(title = "Skins")
@Features({"Big", "Skins"})
@RunWith(Parameterized.class)
public class SkinsTest {
    private static final Properties CONFIG = new Properties();
    private final String urlBig;
    private final String themesUrl;
    private final String saveSkinUrl;

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule;
    private WebDriver driver;
    private CommonMordaSteps user;

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> data() {
        List<Morda> data = new ArrayList<>();
        for (Browser browser : Browser.values()) {
            data.add(mainMorda(RU).withBrowser(browser));
            data.add(comTrMorda().withBrowser(browser));
        }
        return ParametrizationConverter.convert(data);
    }

    private Morda morda;

    public SkinsTest(Morda morda) {
        this.morda = morda;
        this.mordaAllureBaseRule = this.morda.getRule();
        this.driver = mordaAllureBaseRule.getDriver();
        this.user = new CommonMordaSteps(driver);
        urlBig = morda.getUrl(CONFIG.getMordaEnv().getEnv());
        themesUrl = urlBig + "themes/";
        saveSkinUrl = themesUrl + "%s/set?sk=%s";
    }

    @Test
    public void opensThemes() {
        user.opensPage(String.format(themesUrl, CONFIG.getMordaEnv()));
        should(contentLoaded()).whileWaitingUntil(timeoutHasExpired()).matches(driver);
    }

    @Test
    public void opensThemesWithSkin() {
        user.opensPage(String.format(themesUrl, CONFIG.getMordaEnv()) + "glamour/");
        should(contentLoaded()).whileWaitingUntil(timeoutHasExpired()).matches(driver);
    }

    @Test
    public void setSkin() {
        user.opensPage(urlBig);
        setSkin("smile");
        should(contentLoaded()).whileWaitingUntil(timeoutHasExpired()).matches(driver);
    }

    @Test
    public void setSkinSnowl() {
        assumeFalse(morda instanceof ComTrMorda);
        user.opensPage(urlBig);
        setSkin("snowl");
        user.opensPage(String.format(themesUrl, CONFIG.getMordaEnv()));
        should(contentLoaded()).whileWaitingUntil(timeoutHasExpired()).matches(driver);
    }

    private void setSkin(String skinId) {
        user.opensPage(String.format(saveSkinUrl, skinId, CookieManager.getSecretKey(driver)), urlBig);
    }
}
