package ru.yandex.autotests.mainmorda.widgettests.wsettings;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.mainmorda.data.EtrainsSettingsData;
import ru.yandex.autotests.mainmorda.pages.MainPage;
import ru.yandex.autotests.mainmorda.steps.EtrainsSteps;
import ru.yandex.autotests.mainmorda.steps.ModeSteps;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import java.util.Random;

import static org.hamcrest.Matchers.lessThanOrEqualTo;
import static ru.yandex.autotests.mainmorda.data.EtrainsSettingsData.Route;
import static ru.yandex.autotests.mordacommonsteps.utils.Mode.WIDGET;

/**
 * User: eoff
 * Date: 15.01.13
 */
@Aqua.Test(title = "Настройки электричек")
@Features({"Main", "Widget", "Widget Settings"})
@Stories("Etrains")
public class EtrainsSettingsTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private ModeSteps userMode = new ModeSteps(driver);
    private EtrainsSteps userEtrains = new EtrainsSteps(driver);
    private MainPage mainPage = new MainPage(driver);

    @Before
    public void setUp() {
        user.initTest(CONFIG.getBaseURL(), CONFIG.getLang());
        userMode.setMode(WIDGET, mordaAllureBaseRule);
        user.setsRegion(EtrainsSettingsData.REGION);
        userMode.setEditMode(CONFIG.getBaseURL());
        user.shouldSeeElement(mainPage.etrainsBlock);
        user.clicksOn(mainPage.etrainsBlock.editIcon);
        user.shouldSeeElement(mainPage.widgetSettings);
        userEtrains.switchToEtrainsFrame();
        try {
            Thread.sleep(5000L);
        } catch (InterruptedException e) {
            e.printStackTrace();  //To change body of catch statement use File | Settings | File Templates.
        }
        user.shouldSeeElement(mainPage.etrainsSettings);
    }

    @Test
    public void defaultSettings() {
        user.shouldSeeElement(mainPage.etrainsSettings.number);
        user.shouldSeeOptionIsSelected(mainPage.etrainsSettings.number, 4);
        user.shouldSeeElement(mainPage.etrainsSettings.direction);
        user.shouldSeeOptionIsNotSelected(mainPage.etrainsSettings.direction, 0);
        user.shouldSeeElement(mainPage.etrainsSettings.from);
        user.shouldSeeOptionIsNotSelected(mainPage.etrainsSettings.from, 0);
        user.shouldSeeElement(mainPage.etrainsSettings.to);
        user.shouldSeeOptionIsNotSelected(mainPage.etrainsSettings.to, 0);
    }


    @Test
    public void changeCity() {
        user.shouldSeeElement(mainPage.etrainsSettings.city);
        user.selectOption(mainPage.etrainsSettings.city,
                new Random().nextInt(mainPage.etrainsSettings.city.getOptions().size()));
        user.shouldSeeElement(mainPage.etrainsSettings.direction);
        user.shouldSeeOptionIsSelected(mainPage.etrainsSettings.direction, 0);
        user.shouldSeeElement(mainPage.etrainsSettings.from);
        user.shouldSeeOptionIsSelected(mainPage.etrainsSettings.from, 0);
        user.shouldSeeElement(mainPage.etrainsSettings.to);
        user.shouldSeeOptionIsSelected(mainPage.etrainsSettings.to, 0);
    }

    @Test
    public void fromToCorrect() {
        user.shouldSeeElement(mainPage.etrainsSettings.from);
        String from = user.getElementText(mainPage.etrainsSettings.from
                .getFirstSelectedOptionAsHtmlElement());
        user.shouldSeeElement(mainPage.etrainsSettings.to);
        String to = user.getElementText(mainPage.etrainsSettings.to
                .getFirstSelectedOptionAsHtmlElement());
        user.shouldSeeElement(mainPage.etrainsSettings.okButton);
        user.clicksOn(mainPage.etrainsSettings.okButton);
        user.shouldNotSeeElement(mainPage.widgetSettings);
        userEtrains.switchToDefaultContent();
        user.shouldSeeElement(mainPage.widgetSettingsHeader);
        userMode.saveSettings();
        userEtrains.routeTextMatches(from, to);
    }

    @Test
    public void randomRoute() {
        Route route = userEtrains.randomlyFillEtrainsSettings();
        userEtrains.switchToDefaultContent();
        user.shouldSeeElement(mainPage.widgetSettingsHeader);
        userMode.saveSettings();
        userEtrains.routeTextMatches(route.from, route.to);
    }

    @Test
    public void randomSize() {
        user.shouldSeeElement(mainPage.etrainsSettings.number);
        int size = user.selectRandomOption(mainPage.etrainsSettings.number) + 1;
        user.shouldSeeElement(mainPage.etrainsSettings.okButton);
        user.clicksOn(mainPage.etrainsSettings.okButton);
        user.shouldNotSeeElement(mainPage.widgetSettings);
        userEtrains.switchToDefaultContent();
        user.shouldSeeElement(mainPage.widgetSettingsHeader);
        userMode.saveSettings();
        user.shouldSeeListWithSize(mainPage.etrainsBlock.timeTable, lessThanOrEqualTo(size));
    }

    @Test
    public void resetButton() {
        userEtrains.resetButtonWorks();
    }
}
