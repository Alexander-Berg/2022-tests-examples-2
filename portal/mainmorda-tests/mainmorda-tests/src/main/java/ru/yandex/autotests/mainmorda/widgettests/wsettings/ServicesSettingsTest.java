package ru.yandex.autotests.mainmorda.widgettests.wsettings;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.mainmorda.pages.MainPage;
import ru.yandex.autotests.mainmorda.steps.ModeSteps;
import ru.yandex.autotests.mainmorda.steps.ServicesSteps;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import static org.hamcrest.CoreMatchers.equalTo;
import static ru.yandex.autotests.mordacommonsteps.utils.Mode.WIDGET;

/**
 * User: eoff
 * Date: 28.01.13
 */
@Aqua.Test(title = "Настройки блока сервисов")
@Features({"Main", "Widget", "Widget Settings"})
@Stories("Services")
public class ServicesSettingsTest {
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
    public void selectAllButtons() {
        int beforeNew = mainPage.servicesSettings.selectServicesToAdd.getOptions().size();
        int beforeOld = mainPage.servicesSettings.selectServicesToRemove.getOptions().size();
        user.clicksOn(mainPage.servicesSettings.addAllServicesButton);
        user.shouldSeeSelectWithSize(mainPage.servicesSettings.selectServicesToRemove,
                equalTo(beforeNew + beforeOld));
        user.shouldSeeSelectWithSize(mainPage.servicesSettings.selectServicesToAdd,
                equalTo(0));
        user.clicksOn(mainPage.servicesSettings.removeAllServicesButton);
        user.shouldSeeSelectWithSize(mainPage.servicesSettings.selectServicesToRemove,
                equalTo(1));
        user.shouldSeeSelectWithSize(mainPage.servicesSettings.selectServicesToAdd,
                equalTo(beforeNew + beforeOld - 1));
    }

    @Test
    public void addService() {
        user.clicksOn(mainPage.servicesSettings.removeAllServicesButton);
        user.selectRandomOption(mainPage.servicesSettings.selectServicesToAdd);
        user.clicksOn(mainPage.servicesSettings.addOneServiceButton);
        user.selectOption(mainPage.servicesSettings.selectServicesToRemove, 0);
        user.clicksOn(mainPage.servicesSettings.removeOneServiceButton);
        String service =
                mainPage.servicesSettings.selectServicesToRemove.getOptions().get(0).getText();
        user.clicksOn(mainPage.servicesSettings.okButton);
        user.shouldNotSeeElement(mainPage.widgetSettings);
        userMode.saveSettings();
        user.shouldSeeListWithSize(mainPage.servicesBlock.allServices, equalTo(1));
        userService.shouldSeeService(service);
    }
}
