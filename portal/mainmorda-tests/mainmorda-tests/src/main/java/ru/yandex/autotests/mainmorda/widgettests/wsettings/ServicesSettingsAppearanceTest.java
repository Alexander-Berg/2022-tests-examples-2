package ru.yandex.autotests.mainmorda.widgettests.wsettings;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.mainmorda.data.ServicesSettingsData;
import ru.yandex.autotests.mainmorda.pages.MainPage;
import ru.yandex.autotests.mainmorda.steps.ModeSteps;
import ru.yandex.autotests.mainmorda.steps.ServicesSteps;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.autotests.mordacommonsteps.utils.Mode.WIDGET;

/**
 * User: eoff
 * Date: 28.01.13
 */
@Aqua.Test(title = "Внешний вид настроек блока сервисов")
@Features({"Main", "Widget", "Widget Settings"})
@Stories("Services")
public class ServicesSettingsAppearanceTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private ModeSteps userMode = new ModeSteps(driver);
    private ServicesSteps userService = new ServicesSteps(driver);
    private MainPage mainPage = new MainPage(driver);

    @Before
    public void setUp() {
        user.initTest(CONFIG.getBaseURL(), CONFIG.getBaseDomain().getCapital(), CONFIG.getLang());
        userMode.setMode(WIDGET, mordaAllureBaseRule);
        userMode.setEditMode(CONFIG.getBaseURL());
        user.shouldSeeElement(mainPage.servicesBlock);
        user.clicksOn(mainPage.servicesBlock.editIcon);
        user.shouldSeeElement(mainPage.servicesSettings);
    }

    @Test
    public void buttonsTexts() {
        user.shouldSeeElementMatchingTo(mainPage.servicesSettings.addAllServicesButton,
                hasAttribute(HtmlAttribute.VALUE, ServicesSettingsData.ADD_ALL_TEXT));
        user.shouldSeeElementMatchingTo(mainPage.servicesSettings.addOneServiceButton,
                hasAttribute(HtmlAttribute.VALUE, ServicesSettingsData.ADD_TEXT));
        user.shouldSeeElementMatchingTo(mainPage.servicesSettings.removeAllServicesButton,
                hasAttribute(HtmlAttribute.VALUE, ServicesSettingsData.REMOVE_ALL_TEXT));
        user.shouldSeeElementMatchingTo(mainPage.servicesSettings.removeOneServiceButton,
                hasAttribute(HtmlAttribute.VALUE, ServicesSettingsData.REMOVE_TEXT));
    }

    @Test
    public void servicesText() {
        user.shouldSeeElement(mainPage.servicesSettings.servicesTitle);
        userService.shouldSeeServicesTitle(ServicesSettingsData.SERVICES_TITLE_TEXT);
    }
}
