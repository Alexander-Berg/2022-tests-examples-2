package ru.yandex.autotests.mordamobile.all;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.mordamobile.Properties;
import ru.yandex.autotests.mordamobile.blocks.all.AllServicesAllList.ServiceAllItem;
import ru.yandex.autotests.mordamobile.blocks.all.AllServicesTopList.ServiceTopItem;
import ru.yandex.autotests.mordamobile.pages.AllServicesPage;
import ru.yandex.autotests.mordamobile.utils.Service;
import ru.yandex.qatools.allure.annotations.Features;

import java.util.List;

import static ch.lambdaj.Lambda.extract;
import static ch.lambdaj.Lambda.on;
import static ru.yandex.autotests.mordamobile.data.AllServicesData.getAllServicesList;
import static ru.yandex.autotests.mordamobile.data.AllServicesData.getTopServicesList;

/**
 * User: Poluektov Evgeniy <poluektov@yandex-team.ru>
 * on: 05.02.2015.
 */
@Aqua.Test(title = "Проверка количества сервисов")
@Features("All Services")
public class ServicesCountTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private AllServicesPage allServicesPage = new AllServicesPage(driver);

    @Before
    public void setUp() {
        user.opensPage(CONFIG.getBaseURL() + "/all");
        user.shouldSeeElement(allServicesPage.allServicesAllList);
    }

    @Test
    public void servicesTopSize() {
        List<String> expectedServices = extract(getTopServicesList(), on(Service.class).getServiceName());
        List<String> actualServices = extract(allServicesPage.allServicesTopList.items,
                on(ServiceTopItem.class).getServiceName().getText());
        user.shouldSeeItemsInList(actualServices, expectedServices);
    }

    @Test
    public void servicesAllSize() {
        List<String> expectedServices = extract(getAllServicesList(), on(Service.class).getServiceName());
        List<String> actualServices = extract(allServicesPage.allServicesAllList.items,
                on(ServiceAllItem.class).getText());
        user.shouldSeeItemsInList(actualServices, expectedServices);
    }
}
