package ru.yandex.autotests.turkey.all;

import org.junit.Before;
import org.junit.Ignore;
import org.junit.Rule;
import org.junit.Test;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.turkey.Properties;
import ru.yandex.autotests.turkey.blocks.all.AllServicesAllList;
import ru.yandex.autotests.turkey.pages.AllServicesPage;
import ru.yandex.autotests.turkey.steps.AllServicesSteps;
import ru.yandex.qatools.allure.annotations.Features;

import static ch.lambdaj.Lambda.extract;
import static ch.lambdaj.Lambda.on;
import static ru.yandex.autotests.turkey.data.AllServicesData.getExpectedAllOrder;

/**
 * User: Poluektov Evgeniy <poluektov@yandex-team.ru>
 * on: 05.02.2015.
 */
@Aqua.Test(title = "Проверка количества сервисов")
@Features("All Services")
@Ignore
public class ServicesSortTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private AllServicesPage allServicesPage = new AllServicesPage(driver);
    private AllServicesSteps userAll = new AllServicesSteps(driver);

    @Before
    public void setUp() {
        user.opensPage(CONFIG.getBaseURL() + "/all");
        user.shouldSeeElement(allServicesPage.allServicesAllList);
    }

    @Test
    public void servicesAllSort() {
        userAll.shouldSeeServicesInOrder(
                extract(allServicesPage.allServicesAllList.items, on(AllServicesAllList.ServiceAllItem.class).getText()),
                getExpectedAllOrder()
        );
    }
}
