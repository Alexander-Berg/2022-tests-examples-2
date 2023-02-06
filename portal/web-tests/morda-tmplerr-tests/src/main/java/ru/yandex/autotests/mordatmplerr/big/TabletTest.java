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
import ru.yandex.autotests.mordatmplerr.mordatypes.Morda;
import ru.yandex.autotests.utils.morda.ParametrizationConverter;
import ru.yandex.qatools.allure.annotations.Features;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import static ru.yandex.autotests.mordacommonsteps.matchers.DocumentLoadedMatcher.contentLoaded;
import static ru.yandex.autotests.mordatmplerr.mordatypes.MainMorda.mainMorda;
import static ru.yandex.autotests.mordatmplerr.mordatypes.TouchType.TABLET;
import static ru.yandex.autotests.utils.morda.url.Domain.RU;
import static ru.yandex.qatools.htmlelements.matchers.MatcherDecorators.should;
import static ru.yandex.qatools.htmlelements.matchers.MatcherDecorators.timeoutHasExpired;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 19.03.14
 */

@Aqua.Test(title = "Tablet")
@Features({"Big", "Tablet"})
@RunWith(Parameterized.class)
public class TabletTest {
    private static final Properties CONFIG = new Properties();
    private final String urlBig;
    private final String urlEdit;

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule;
    private WebDriver driver;
    private CommonMordaSteps user;

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> data() {
        List<Morda> data = new ArrayList<>();
        data.add(mainMorda(RU).withTouchType(TABLET));
        return ParametrizationConverter.convert(data);
    }

    private Morda morda;

    public TabletTest(Morda morda) {
        this.morda = morda;
        this.mordaAllureBaseRule = this.morda.getRule();
        this.driver = mordaAllureBaseRule.getDriver();
        this.user = new CommonMordaSteps(driver);
        urlBig = morda.getUrl(CONFIG.getMordaEnv().getEnv());
        urlEdit = urlBig + "?edit=1";
    }

    @Test
    public void tabletMainPage() {
        user.opensPage(urlBig);
        should(contentLoaded()).whileWaitingUntil(timeoutHasExpired()).matches(driver);
    }

    @Test
    public void tabletEditPage() {
        user.opensPage(urlEdit);
        should(contentLoaded()).whileWaitingUntil(timeoutHasExpired()).matches(driver);
    }
}
