package ru.yandex.autotests.mainmorda.widgettests.services;

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
import ru.yandex.autotests.mainmorda.steps.ServicesSteps;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.mordaexportsclient.beans.ServicesV122Entry;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import static org.hamcrest.Matchers.notNullValue;
import static org.junit.Assume.assumeThat;
import static ru.yandex.autotests.mordacommonsteps.utils.Mode.WIDGET;
import static ru.yandex.autotests.mordaexportslib.data.ServicesData.getServices;

/**
 * User: eoff
 * Date: 30.01.13
 */
@Aqua.Test(title = "Проверка ссылок всех сервисов в виджете")
@RunWith(Parameterized.class)
@Features({"Main", "Widget", "Services Block"})
@Stories("Links")
public class ServicesLinksTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private ModeSteps userMode = new ModeSteps(driver);
    private ServicesSteps userService = new ServicesSteps(driver);
    private MainPage mainPage = new MainPage(driver);
    private ServicesV122Entry service;

    public ServicesLinksTest(String name, ServicesV122Entry service) {
        this.service = service;
    }

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> testData() {
        List<Object[]> data = new ArrayList<>();
        List<ServicesV122Entry> services = getServices(CONFIG.getBaseDomain(), "4");
        for (ServicesV122Entry e : services) {
            data.add(new Object[]{e.getId(), e});
        }
        return data;
    }

    @Before
    public void setUp() {
        user.initTest(CONFIG.getBaseURL(), CONFIG.getBaseDomain().getCapital(), CONFIG.getLang());
        userMode.setMode(WIDGET, mordaAllureBaseRule);
        userMode.setEditMode(CONFIG.getBaseURL());
        user.shouldSeeElement(mainPage.servicesBlock);
        user.clicksOn(mainPage.servicesBlock.editIcon);
        user.shouldSeeElement(mainPage.servicesSettings);
        user.clicksOn(mainPage.servicesSettings.addAllServicesButton);
        user.clicksOn(mainPage.servicesSettings.okButton);
        user.shouldNotSeeElement(mainPage.servicesSettings);
        userMode.saveSettings();
    }

    @Test
    public void serviceLink() {
        HtmlElement serviceLink = userService.findServiceOnPageSafely(mainPage.servicesBlock.allServices, service.getId());
        assumeThat(serviceLink, notNullValue());
        userService.shouldSeeServiceWithOutComment(serviceLink, service);
    }
}