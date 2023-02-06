package ru.yandex.autotests.mainmorda.commontests.services;

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

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import static ru.yandex.autotests.mordaexportslib.data.ServicesData.getNoSignServices;

/**
 * User: eoff
 * Date: 12.12.12
 */
@Aqua.Test(title = "Сервисы без Подписей")
@RunWith(Parameterized.class)
@Features({"Main", "Common", "Services Block"})
@Stories("No Sign Services")
public class ServicesNoSignTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private ModeSteps userMode = new ModeSteps(driver);
    private ServicesSteps userService = new ServicesSteps(driver);
    private MainPage mainPage = new MainPage(driver);

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> testData() {
        List<Object[]> data = new ArrayList<>();
        for (ServicesV122Entry e : getNoSignServices(CONFIG.getBaseDomain().getCapital(), "v12")) {
            data.add(new Object[]{e.getId(), e});
        }
        return data;
    }

    private ServicesV122Entry service;

    public ServicesNoSignTest(String name, ServicesV122Entry service) {
        this.service = service;
    }

    @Before
    public void setUp() {
        user.initTest(CONFIG.getBaseURL(), CONFIG.getBaseDomain().getCapital(), CONFIG.getLang());
        userMode.setMode(CONFIG.getMode(), mordaAllureBaseRule);
        user.shouldSeeElement(mainPage.servicesBlock);
    }

    @Test
    public void serviceLink() {
        userService.shouldSeeServiceWithOutComment(service);
    }
}
