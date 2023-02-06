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

import static ru.yandex.autotests.turkey.data.AllServicesData.COMPANY_LINK;
import static ru.yandex.autotests.turkey.data.AllServicesData.HELP_LINK;
import static ru.yandex.autotests.turkey.data.AllServicesData.YANDEX_LINK;

/**
 * User: Poluektov Evgeniy <poluektov@yandex-team.ru>
 * on: 26.02.2015.
 */
@Aqua.Test(title = "Footer на странице всех сервисов")
@Features("All Services")
@Stories("Footer")
public class FooterTest {
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
    public void helpLink() {
        user.shouldSeeLinkLight(allServicesPage.allServicesFooter.helpLink, HELP_LINK);
    }

    @Test
    public void companyLink() {
        user.shouldSeeLinkLight(allServicesPage.allServicesFooter.companyLink, COMPANY_LINK);
    }

    @Test
    public void yandexLink() {
        user.shouldSeeLinkLight(allServicesPage.allServicesFooter.yandexLink, YANDEX_LINK);
    }
}
