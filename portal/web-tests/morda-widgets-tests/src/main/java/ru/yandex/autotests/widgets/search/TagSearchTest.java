package ru.yandex.autotests.widgets.search;

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
import ru.yandex.autotests.widgets.steps.CategorySteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.htmlelements.element.HtmlElement;
import ru.yandex.qatools.selenium.grid.GridClient;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import static org.openqa.selenium.remote.DesiredCapabilities.firefox;
import static ru.yandex.autotests.utils.morda.ParametrizationConverter.convert;

/**
 * User: leonsabr
 * Date: 08.11.11
 * Выдача по тегам не пустая.
 */
@Aqua.Test(title = "Поиск по тегам")
@Features("Search")
@RunWith(Parameterized.class)
public class TagSearchTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private WidgetPage widgetPage = new WidgetPage(driver);
    private CategorySteps userCategory = new CategorySteps(driver);

    @Parameterized.Parameters
    public static Collection<Object[]> testData() {
        WebDriver driver = new GridClient().find(firefox());
        WidgetPage page = new WidgetPage(driver);

        driver.get(CONFIG.getBaseURL());

        List<String> tags = new ArrayList<String>();
        for (HtmlElement element : page.allTags) {
            tags.add(element.getText());
        }

        driver.quit();
        return convert(tags);
    }

    private String tag;

    public TagSearchTest(String tag) {
        this.tag = tag;
    }

    @Before
    public void setUp() {
        user.opensPage(CONFIG.getBaseURL());
    }

    @Test
    public void tagSearch() {
        userCategory.shouldSeeTag(widgetPage.allTags, tag);
    }
}
