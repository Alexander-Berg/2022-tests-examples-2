package ru.yandex.autotests.mainmorda.widgettests.wsettings;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.mainmorda.data.WeatherSettingsData;
import ru.yandex.autotests.mainmorda.pages.MainPage;
import ru.yandex.autotests.mainmorda.steps.ModeSteps;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.utils.morda.ParametrizationConverter;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import java.util.Collection;

import static org.hamcrest.CoreMatchers.equalTo;
import static ru.yandex.autotests.mordacommonsteps.utils.Mode.WIDGET;

/**
 * User: eoff
 * Date: 19.12.12
 */
@Aqua.Test(title = "Сохранение города в настройках погоды")
@RunWith(Parameterized.class)
@Features({"Main", "Widget", "Widget Settings"})
@Stories("Weather")
public class WeatherSettingsSaveCityTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private ModeSteps userMode = new ModeSteps(driver);
    private MainPage mainPage = new MainPage(driver);

    @Parameterized.Parameters
    public static Collection<Object[]> data() {
        return ParametrizationConverter.convert(WeatherSettingsData.CITIES_INPUT);
    }

    private String city;

    public WeatherSettingsSaveCityTest(String city) {
        this.city = city;
    }

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
    public void setCity() {
        user.clearsInput(mainPage.weatherSettings.regionInput);
        user.entersTextInInput(mainPage.weatherSettings.regionInput, "");
        user.entersTextInInput(mainPage.weatherSettings.regionInput, city);
        user.shouldSeeElement(mainPage.weatherSettings.firstSuggest);
        user.clicksOn(mainPage.weatherSettings.firstSuggest);
        user.shouldNotSeeElement(mainPage.weatherSettings.firstSuggest);
        user.clicksOn(mainPage.widgetSettings.okButton);
        user.shouldNotSeeElement(mainPage.widgetSettings);
        user.shouldSeeElement(mainPage.weatherBlock.city);
        user.shouldSeeElementWithText(mainPage.weatherBlock.city,
                equalTo("(" + WeatherSettingsData.CITIES_TRANSLATIONS.get(city) + ")"));
    }
}
