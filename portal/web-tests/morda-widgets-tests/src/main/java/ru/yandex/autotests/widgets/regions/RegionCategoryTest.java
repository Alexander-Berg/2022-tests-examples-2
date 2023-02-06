package ru.yandex.autotests.widgets.regions;

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
import ru.yandex.autotests.widgets.steps.RegionSteps;
import ru.yandex.qatools.allure.annotations.Features;

import java.util.Collection;

import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.autotests.utils.morda.ParametrizationConverter.convert;
import static ru.yandex.autotests.widgets.data.RegionsData.REGION_CATEGORIES;
import static ru.yandex.autotests.widgets.data.RegionsData.RegionCategories;

/**
 * User: leonsabr
 * Date: 08.11.11
 * Для выставленного региона в списке рубрик появляются разделы с виджетами для города/райцентра-области/страны.
 */
@Aqua.Test(title = "Виджеты города и области в рубриках")
@Features("Regions Categories")
@RunWith(Parameterized.class)
public class RegionCategoryTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private RegionSteps userRegion = new RegionSteps(driver);
    private WidgetPage widgetPage = new WidgetPage(driver);

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> testData() {
        return convert(REGION_CATEGORIES);
    }

    private RegionCategories regionCategories;

    public RegionCategoryTest(RegionCategories regionCategories) {
        this.regionCategories = regionCategories;
    }

    @Before
    public void setUp() {
        user.opensPage(CONFIG.getBaseURL());
        user.setsRegion(regionCategories.getRegion(), CONFIG.getBaseURL());
    }

    @Test
    public void regionCategoriesSize() {
        user.shouldSeeListWithSize(widgetPage.regionalCategories,
                equalTo(regionCategories.getRegions().size()));
    }

    @Test
    public void regionCategories() {
        userRegion.shouldSeeRegionalCategories(regionCategories);
    }
}
