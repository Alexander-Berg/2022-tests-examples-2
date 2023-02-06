package ru.yandex.autotests.widgets.search;

import org.junit.After;
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

import java.util.Collection;

import static ru.yandex.autotests.utils.morda.ParametrizationConverter.convert;
import static ru.yandex.autotests.widgets.data.SearchData.Category;

/**
 * User: leonsabr
 * Date: 08.11.11
 * Выдача по рубрикам не пустая.
 */
@Aqua.Test(title = "Поиск по рубрикам")
@Features("Search")
@RunWith(Parameterized.class)
public class CategoriesTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private CategorySteps userCategory = new CategorySteps(driver);
    private WidgetPage widgetPage = new WidgetPage(driver);

    @Parameterized.Parameters
    public static Collection<Object[]> testData() {
        return convert(Category.values());
    }

    private Category category;

    public CategoriesTest(Category category) {
        this.category = category;
    }

    @Before
    public void setUp() {
        user.initTest(CONFIG.getBaseURL(), CONFIG.getBaseDomain().getCapital(), CONFIG.getLang());
    }

    @Test
    public void categorySearch() {
        userCategory.shouldSeeCategory(widgetPage.allCategories, category);
    }

    @Test
    public void categorySelects() {
        userCategory.shouldSeeCategorySelects(widgetPage.allCategories, category);
    }

    @After
    public void closeDriver() {
        driver.quit();
    }
}
