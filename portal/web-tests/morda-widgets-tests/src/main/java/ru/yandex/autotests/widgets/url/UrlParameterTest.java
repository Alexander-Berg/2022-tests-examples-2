package ru.yandex.autotests.widgets.url;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.widgets.Properties;
import ru.yandex.autotests.widgets.pages.WidgetPage;
import ru.yandex.qatools.allure.annotations.Features;

import java.util.Arrays;
import java.util.Collection;

import static org.hamcrest.Matchers.containsString;
import static ru.yandex.autotests.utils.morda.ParametrizationConverter.convert;

/**
 * User: leonsabr
 * Date: 29.11.11
 * Параметр url сохраняется при навигации по выдаче.
 */
@Aqua.Test(title = "Параметр url сохраняется при навигации по выдаче")
@Features("Search By URL")
@RunWith(Parameterized.class)
public class UrlParameterTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private WidgetPage widgetPage = new WidgetPage(driver);

    @Parameterized.Parameters
    public static Collection<Object[]> testData() {
        return convert(Arrays.asList("yandex.ru", "livejournal.com"));
    }

    private String url;

    public UrlParameterTest(String url) {
        this.url = CONFIG.getBaseURL() + "/?url=" + url;
    }

    @Before
    public void setUp() {
        user.initTest(CONFIG.getBaseURL(), CONFIG.getBaseDomain().getCapital(), CONFIG.getLang());
    }

    @Test
    public void urlPassedInPager() {
        user.opensPage(url);
        user.shouldSeeElement(widgetPage.nextPageButton);
        user.clicksOn(widgetPage.nextPageButton);
        user.shouldSeePage(containsString(url));

    }
}
