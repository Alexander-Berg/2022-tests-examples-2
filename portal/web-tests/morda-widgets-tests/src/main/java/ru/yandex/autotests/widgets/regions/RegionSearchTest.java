package ru.yandex.autotests.widgets.regions;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.utils.morda.ParametrizationConverter;
import ru.yandex.autotests.widgets.Properties;
import ru.yandex.autotests.widgets.pages.WidgetPage;
import ru.yandex.autotests.widgets.steps.RegionSteps;
import ru.yandex.qatools.allure.annotations.Features;

import java.util.Collection;

import static org.hamcrest.Matchers.greaterThan;
import static org.hamcrest.Matchers.not;
import static ru.yandex.autotests.widgets.data.RegionsData.WIDGET_REGIONS_LIST;
import static ru.yandex.autotests.widgets.data.RegionsData.WidgetRegions;
import static ru.yandex.autotests.widgets.data.SearchData.WIDGETS_NUMBER_MATCHER;

/**
 * User: leonsabr
 * Date: 15.11.11
 * Проверка поиска /?region=id
 */
@Aqua.Test(title = "Поиск по id региона")
@Features("Regions Search")
@RunWith(Parameterized.class)
public class RegionSearchTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private RegionSteps userRegion = new RegionSteps(driver);
    private WidgetPage widgetPage = new WidgetPage(driver);

    private WidgetRegions widgetRegions;

    public RegionSearchTest(WidgetRegions widgetRegions) {
        this.widgetRegions = widgetRegions;
    }

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> data() {
        return ParametrizationConverter.convert(WIDGET_REGIONS_LIST);
    }

    @Before
    public void setUp() {
        user.opensPage(CONFIG.getBaseURL() + "/?region=" + widgetRegions.getRegion().getRegionId());
    }

    @Test
    public void searchResultByRegion() {
        user.shouldSeeListWithSize(widgetPage.allWidgets, greaterThan(0));

        user.shouldSeeElementWithText(widgetPage.title, not(""));

        user.shouldSeeElementWithText(widgetPage.widgetsAmount, WIDGETS_NUMBER_MATCHER);

        userRegion.shouldSeeWidgetRegions(widgetPage.allRegions, widgetRegions.getRegionMatcher());
    }
}