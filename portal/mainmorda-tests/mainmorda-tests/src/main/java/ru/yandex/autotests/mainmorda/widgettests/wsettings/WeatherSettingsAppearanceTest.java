package ru.yandex.autotests.mainmorda.widgettests.wsettings;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.mainmorda.data.WeatherSettingsData;
import ru.yandex.autotests.mainmorda.pages.MainPage;
import ru.yandex.autotests.mainmorda.steps.ModeSteps;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import static org.hamcrest.CoreMatchers.equalTo;
import static org.hamcrest.CoreMatchers.not;
import static ru.yandex.autotests.mordacommonsteps.utils.Mode.WIDGET;

/**
 * User: eoff
 * Date: 19.12.12
 */
@Aqua.Test(title = "Внешний вид настроек погоды")
@Features({"Main", "Widget", "Widget Settings"})
@Stories("Weather")
public class WeatherSettingsAppearanceTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private ModeSteps userMode = new ModeSteps(driver);
    private MainPage mainPage = new MainPage(driver);

    @Before
    public void setUp() {
        user.initTest(CONFIG.getBaseURL(), CONFIG.getBaseDomain().getCapital(), CONFIG.getLang());
        userMode.setMode(WIDGET, mordaAllureBaseRule);
        userMode.setEditMode(CONFIG.getBaseURL());
        user.shouldSeeElement(mainPage.weatherBlock);
        user.clicksOn(mainPage.weatherBlock.editIcon);
        user.shouldSeeElement(mainPage.weatherSettings);
    }

    @Test
    public void regionText() {
        user.shouldSeeElement(mainPage.weatherSettings.regionLabel);
        user.shouldSeeElementWithText(mainPage.weatherSettings.regionLabel,
                WeatherSettingsData.REGION_TEXT);
    }

    @Test
    public void seeRegionInput() {
        user.shouldSeeElement(mainPage.weatherSettings.regionInput);
        user.shouldSeeInputWithText(mainPage.weatherSettings.regionInput,
                not(equalTo("")));
    }
}
