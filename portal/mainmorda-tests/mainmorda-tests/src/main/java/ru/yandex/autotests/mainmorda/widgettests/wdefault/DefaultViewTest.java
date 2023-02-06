package ru.yandex.autotests.mainmorda.widgettests.wdefault;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.mainmorda.pages.MainPage;
import ru.yandex.autotests.mainmorda.steps.ModeSteps;
import ru.yandex.autotests.mainmorda.steps.WidgetSteps;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.utils.morda.ParametrizationConverter;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.qatools.allure.annotations.Features;

import java.util.Collection;

import static ru.yandex.autotests.mainmorda.data.WidgetsData.REGIONS_FOR_DDEFAULT_WIDGET_TESTING;
import static ru.yandex.autotests.mainmorda.data.WidgetsData.WIDGETS_SETS_FOR_REGIONS;
import static ru.yandex.autotests.mordacommonsteps.utils.Mode.WIDGET;

/**
 * User: alex89
 * Date: 14.01.13
 */

@Aqua.Test(title = "Виджеты по-умолчанию в различных регионах")
@RunWith(Parameterized.class)
@Features({"Main", "Widget", "Widgets Default"})
public class DefaultViewTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private ModeSteps userMode = new ModeSteps(driver);
    private WidgetSteps userWidget = new WidgetSteps(driver);
    private MainPage mainPage = new MainPage(driver);

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> testData() {
        return ParametrizationConverter.convert(REGIONS_FOR_DDEFAULT_WIDGET_TESTING.get(CONFIG.getBaseDomain()));
    }

    private Region region;

    public DefaultViewTest(Region region) {
        this.region = region;
    }

    @Before
    public void before() {
        user.initTest(CONFIG.getBaseURL(), CONFIG.getLang());
        user.setsRegion(region);
        userMode.setMode(WIDGET, mordaAllureBaseRule);
    }

    @Test
    public void setOfDefaultWidgetsIsCorrectForRegion() {
        userWidget.shouldSeeWidgets(WIDGETS_SETS_FOR_REGIONS.get(region));
        userMode.setEditMode();
        userWidget.shouldSeeWidgets(WIDGETS_SETS_FOR_REGIONS.get(region));
    }
}
