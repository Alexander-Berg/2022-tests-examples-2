package ru.yandex.autotests.mainmorda.widgettests.wsettings;

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
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.utils.morda.ParametrizationConverter;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import java.util.Collection;

import static ru.yandex.autotests.mordacommonsteps.utils.Mode.WIDGET;

/**
 * User: eoff
 * Date: 19.12.12
 */
@Aqua.Test(title = "Саджест в настройках погоды")
@RunWith(Parameterized.class)
@Features({"Main", "Widget", "Widget Settings"})
@Stories("Weather")
public class WeatherSettingsSuggestTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private ModeSteps userMode = new ModeSteps(driver);
    private MainPage mainPage = new MainPage(driver);

    @Parameterized.Parameters
    public static Collection<Object[]> data() {
        return ParametrizationConverter.convert(new String[]{
                "vjc",
                "мос",
                "mos"
        });
    }

    private String request;

    public WeatherSettingsSuggestTest(String request) {
        this.request = request;
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
    public void suggestAppears() {
        user.shouldSeeElement(mainPage.weatherSettings.regionInput);
        user.clearsInput(mainPage.weatherSettings.regionInput);
        user.entersTextInInput(mainPage.weatherSettings.regionInput, "");
        user.clicksOn(mainPage.weatherSettings.setupTitle);
        user.shouldNotSeeElement(mainPage.weatherSettings.suggest);
        user.entersTextInInput(mainPage.weatherSettings.regionInput, request);
        user.shouldSeeElement(mainPage.weatherSettings.suggest);
        user.clearsInput(mainPage.weatherSettings.regionInput);
        user.entersTextInInput(mainPage.weatherSettings.regionInput, "");
        user.clicksOn(mainPage.weatherSettings.setupTitle);
        user.clicksOn(mainPage.weatherSettings.regionLabel);
        user.shouldNotSeeElement(mainPage.weatherSettings.suggest);
    }
}
