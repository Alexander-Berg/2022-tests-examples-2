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
import ru.yandex.autotests.utils.morda.ParametrizationConverter;
import ru.yandex.qatools.allure.annotations.Features;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import static ru.yandex.autotests.mordacommonsteps.matchers.DocumentLoadedMatcher.contentLoaded;
import static ru.yandex.autotests.mordatmplerr.mordatypes.MainMorda.familyMorda;
import static ru.yandex.autotests.mordatmplerr.mordatypes.MainMorda.mainMorda;
import static ru.yandex.autotests.utils.morda.url.Domain.RU;
import static ru.yandex.qatools.htmlelements.matchers.MatcherDecorators.should;
import static ru.yandex.qatools.htmlelements.matchers.MatcherDecorators.timeoutHasExpired;


@Aqua.Test(title = "Vertical Banner")
@Features({"Big", "Vertical Banner"})
@RunWith(Parameterized.class)
public class BannerTest {
    private static final Properties CONFIG = new Properties();
    private final String url;

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule;
    private WebDriver driver;
    private CommonMordaSteps user;

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> data() {
        List<Morda> data = new ArrayList<>();
        for (Browser browser : Browser.values()) {
            data.add(mainMorda(RU).withBrowser(browser));
            data.add(familyMorda(RU).withBrowser(browser));
        }
        return ParametrizationConverter.convert(data);
    }

    private Morda morda;

    public BannerTest(Morda morda) {
        this.morda = morda;
        this.mordaAllureBaseRule = this.morda.getRule();
        this.driver = mordaAllureBaseRule.getDriver();
        this.user = new CommonMordaSteps(driver);
        url = morda.getUrl(CONFIG.getMordaEnv().getEnv());
    }

    @Test
    public void verticalBanner() throws InterruptedException {
        user.opensPage(url);
        user.resizeWindow(1280, 1024);
        user.opensPage(url + "?awad=249870");
        should(contentLoaded()).whileWaitingUntil(timeoutHasExpired()).matches(driver);
    }
}
