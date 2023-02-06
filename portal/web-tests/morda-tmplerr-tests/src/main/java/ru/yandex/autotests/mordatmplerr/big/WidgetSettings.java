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
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.qatools.allure.annotations.Features;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collection;
import java.util.List;

import static ru.yandex.autotests.mordacommonsteps.matchers.DocumentLoadedMatcher.contentLoaded;
import static ru.yandex.autotests.mordatmplerr.mordatypes.MainMorda.mainMorda;
import static ru.yandex.autotests.utils.morda.url.Domain.RU;
import static ru.yandex.qatools.htmlelements.matchers.MatcherDecorators.should;
import static ru.yandex.qatools.htmlelements.matchers.MatcherDecorators.timeoutHasExpired;


@Aqua.Test(title = "Widget Settings")
@Features({"Big", "Widget Settings"})
@RunWith(Parameterized.class)
public class WidgetSettings {
    private static final Properties CONFIG = new Properties();
    private static final List<String> WIDGETS = Arrays.asList(
            "weather", "traffic", "services", "tvafisha", "stocks", "etrains"
    );
    private String urlBig;
    private String urlSettings;

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule;

    private WebDriver driver;
    private CommonMordaSteps user;

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> data() {
        List<Object[]> data = new ArrayList<>();
        for (String widget : WIDGETS) {
            for (Browser browser : Browser.values()) {
                data.add(new Object[]{
                        widget,
                        mainMorda(RU).withBrowser(browser)
                });
            }
        }
        return data;
    }

    private Morda morda;

    public WidgetSettings(String widget, Morda morda) {
        this.morda = morda;
        this.mordaAllureBaseRule = this.morda.getRule();
        this.driver = mordaAllureBaseRule.getDriver();
        this.user = new CommonMordaSteps(driver);
        urlBig = morda.getUrl(CONFIG.getMordaEnv().getEnv());
        urlSettings = urlBig + "?edit=1#open=_" + widget;
    }

    @Test
    public void widgetSettings() {
        user.opensPage(urlBig);
        user.setsRegion(Region.DUBNA, urlBig);
        user.opensPage(urlSettings);
        should(contentLoaded()).whileWaitingUntil(timeoutHasExpired()).matches(driver);
    }
}
