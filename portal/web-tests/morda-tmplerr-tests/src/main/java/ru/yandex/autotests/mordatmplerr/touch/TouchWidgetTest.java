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
import ru.yandex.autotests.utils.morda.ParametrizationConverter;
import ru.yandex.qatools.allure.annotations.Features;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import static ru.yandex.autotests.mordacommonsteps.matchers.DocumentLoadedMatcher.contentLoaded;
import static ru.yandex.autotests.mordatmplerr.mordatypes.Browser.CHROME;
import static ru.yandex.autotests.mordatmplerr.mordatypes.ComTrMorda.comTrMorda;
import static ru.yandex.autotests.mordatmplerr.mordatypes.MainMorda.mainMorda;
import static ru.yandex.autotests.mordatmplerr.mordatypes.TouchType.ANDROID_CHROME;
import static ru.yandex.autotests.mordatmplerr.mordatypes.TouchType.IPHONE_SAFARI;
import static ru.yandex.autotests.utils.morda.url.Domain.RU;
import static ru.yandex.qatools.htmlelements.matchers.MatcherDecorators.should;
import static ru.yandex.qatools.htmlelements.matchers.MatcherDecorators.timeoutHasExpired;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 08.04.14
 */

@Aqua.Test(title = "Add Widget")
@Features({"Touch", "Add Widget"})
@RunWith(Parameterized.class)
public class TouchWidgetTest {

    private static final Properties CONFIG = new Properties();
    private final String url;

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule;
    private WebDriver driver;
    private CommonMordaSteps user;

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> data() {
        List<Morda> data = new ArrayList<>();
        data.add(mainMorda(RU).withTouchType(IPHONE_SAFARI).withBrowser(CHROME));
        data.add(comTrMorda().withTouchType(ANDROID_CHROME).withBrowser(CHROME));
        return ParametrizationConverter.convert(data);
    }

    private Morda morda;

    public TouchWidgetTest(Morda morda) {
        this.morda = morda;
        this.mordaAllureBaseRule = this.morda.getRule();
        this.driver = mordaAllureBaseRule.getDriver();
        this.user = new CommonMordaSteps(driver);
        url = morda.getUrl(CONFIG.getMordaEnv().getEnv());
    }

    @Test
    public void tryAddWidget() {
        user.opensPage(url + "?add=8483");
        should(contentLoaded()).whileWaitingUntil(timeoutHasExpired()).matches(driver);
    }
}
