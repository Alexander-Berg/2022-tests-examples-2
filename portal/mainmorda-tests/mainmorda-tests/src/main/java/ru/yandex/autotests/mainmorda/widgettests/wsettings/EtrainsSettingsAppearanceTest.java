package ru.yandex.autotests.mainmorda.widgettests.wsettings;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.mainmorda.data.CommonSettingsData;
import ru.yandex.autotests.mainmorda.data.EtrainsSettingsData;
import ru.yandex.autotests.mainmorda.pages.MainPage;
import ru.yandex.autotests.mainmorda.steps.EtrainsSteps;
import ru.yandex.autotests.mainmorda.steps.ModeSteps;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import static org.hamcrest.CoreMatchers.equalTo;
import static org.hamcrest.Matchers.greaterThan;
import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.autotests.mordacommonsteps.utils.Mode.WIDGET;

/**
 * User: eoff
 * Date: 14.01.13
 */
@Aqua.Test(title = "Внешний вид настроек электричек")
@Features({"Main", "Widget", "Widget Settings"})
@Stories("Etrains")
public class EtrainsSettingsAppearanceTest {
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
    }

    @Test
    public void city() {
        user.shouldSeeElement(mainPage.etrainsSettings.city);
        user.shouldSeeSelectWithSize(mainPage.etrainsSettings.city, greaterThan(0));
    }

    @Test
    public void direction() {
        user.shouldSeeElement(mainPage.etrainsSettings.direction);
        user.shouldSeeSelectWithSize(mainPage.etrainsSettings.direction, greaterThan(0));
    }

    @Test
    public void from() {
        user.shouldSeeElement(mainPage.etrainsSettings.from);
        user.shouldSeeSelectWithSize(mainPage.etrainsSettings.from,
                greaterThan(0));
    }

    @Test
    public void to() {
        user.shouldSeeElement(mainPage.etrainsSettings.to);
        user.shouldSeeSelectWithSize(mainPage.etrainsSettings.to, greaterThan(0));
    }

    @Test
    public void number() {
        user.shouldSeeElement(mainPage.etrainsSettings.number);
        user.shouldSeeSelectWithSize(mainPage.etrainsSettings.number, equalTo(10));
        userEtrains.shouldSeeNumberSelectText();
    }

    @Test
    public void closeButtonText() {
        user.shouldSeeElement(mainPage.etrainsSettings.closeSettingsButton);
        user.shouldSeeElementMatchingTo(mainPage.etrainsSettings.closeSettingsButton,
                hasAttribute(HtmlAttribute.VALUE, EtrainsSettingsData.CLOSE_TEXT));
    }

    @Test
    public void okButtonText() {
        user.shouldSeeElement(mainPage.etrainsSettings.okButton);
        user.shouldSeeElementMatchingTo(mainPage.etrainsSettings.okButton,
                hasAttribute(HtmlAttribute.VALUE, EtrainsSettingsData.OK_TEXT));
    }

    @Test
    public void resetButtonText() {
        user.shouldSeeElement(mainPage.etrainsSettings.resetSettingsButton);
        user.shouldSeeElementMatchingTo(mainPage.etrainsSettings.resetSettingsButton,
                hasAttribute(HtmlAttribute.VALUE, EtrainsSettingsData.RESET_TEXT));
    }

    @Test
    public void setupTitleText() {
        userEtrains.switchToDefaultContent();
        user.shouldSeeElement(mainPage.etrainsSettings.setupTitle);
        user.shouldSeeElementWithText(mainPage.etrainsSettings.setupTitle,
                CommonSettingsData.SETTINGS_TITLE);
    }

    @Test
    public void closeCross() {
        userEtrains.switchToDefaultContent();
        user.shouldSeeElement(mainPage.etrainsSettings.closeSettingsX);
        user.clicksOn(mainPage.etrainsSettings.closeSettingsX);
    }

}
