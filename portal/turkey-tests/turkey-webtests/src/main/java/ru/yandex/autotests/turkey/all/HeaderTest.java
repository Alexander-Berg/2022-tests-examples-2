package ru.yandex.autotests.turkey.all;


import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.turkey.Properties;
import ru.yandex.autotests.turkey.pages.AllServicesPage;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import static ru.yandex.autotests.turkey.data.AllServicesData.*;


/**
 * Created with IntelliJ IDEA.
 * User: arttimofeev
 * Date: 27.08.12
 */

@Aqua.Test(title = "Header на странице всех сервисов")
@Features("All Services")
@Stories("Header")
public class HeaderTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private AllServicesPage allServicesPage = new AllServicesPage(driver);

    @Before
    public void setUp() {
        user.opensPage(CONFIG.getBaseURL() + "/all");
    }

    @Test
    public void logo() {
        user.shouldSeeLinkLight(allServicesPage.allServicesHeader.mainPageLink, LOGO_LINK);
    }

    @Test
    public void mobileAppsLink() {
        user.shouldSeeLinkLight(allServicesPage.allServicesHeader.mobileLink, MOBILE_APPS_LINK);
    }

    @Test
    public void mobileSitesText() {
        user.shouldSeeElement(allServicesPage.allServicesHeader.programsLink);
        user.shouldSeeElementWithText(allServicesPage.allServicesHeader.programsLink, PC_PROGRAMS_TEXT_MATCHER);
    }
}
