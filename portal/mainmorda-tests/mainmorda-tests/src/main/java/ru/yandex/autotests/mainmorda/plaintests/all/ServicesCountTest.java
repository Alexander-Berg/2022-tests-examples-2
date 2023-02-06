package ru.yandex.autotests.mainmorda.plaintests.all;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.mainmorda.pages.AllServicesPage;
import ru.yandex.autotests.mainmorda.utils.Service;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import java.util.ArrayList;
import java.util.List;

import static ch.lambdaj.Lambda.extract;
import static ch.lambdaj.Lambda.on;
import static ru.yandex.autotests.mainmorda.blocks.all.AllServicesAllList.ServiceAllItem;
import static ru.yandex.autotests.mainmorda.data.AllServicesData.getAllServicesList;
import static ru.yandex.autotests.mainmorda.data.AllServicesData.getBottomServicesList;
import static ru.yandex.autotests.mainmorda.data.AllServicesData.getSpecialServicesList;
import static ru.yandex.autotests.mainmorda.data.AllServicesData.getTopServicesList;

/**
 * User: Poluektov Evgeniy <poluektov@yandex-team.ru>
 * on: 26.02.2015.
 */
@Aqua.Test(title = "Проверка кол-ва сервисов")
@Features({"Main", "Plain", "All"})
public class ServicesCountTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private AllServicesPage allServicesPage = new AllServicesPage(driver);

    @Before
    public void setUp() {
        user.initTest(CONFIG.getBaseURL(), CONFIG.getBaseDomain().getCapital(), CONFIG.getLang());
        user.opensPage(CONFIG.getBaseURL() + "/all");
        user.shouldSeeElement(allServicesPage.allServicesAllList);
    }

    @Test
    public void servicesTopSize() {
        List<String> expectedServices = extract(getTopServicesList(), on(Service.class).getServiceName());
        List<String> actualServices =  new ArrayList<>();
        for (HtmlElement item : allServicesPage.allServicesTopList.items ) {
            String text = item.getText();
            text = text.split("\\n")[0];
            if (!text.equals("")) {
                actualServices.add(text);
            }
        }
        user.shouldSeeItemsInList(actualServices, expectedServices);
    }

    @Test
    public void servicesBottomSize() {
        List<String> expectedServices = extract(getBottomServicesList(), on(Service.class).getServiceName());
        List<String> actualServices =  new ArrayList<>();
        for (HtmlElement item : allServicesPage.allServicesBottomList.items ) {
            String text = item.getText();
            text = text.split("\\n")[0];
            if (!text.equals("")) {
                actualServices.add(text);
            }
        }
        user.shouldSeeItemsInList(actualServices, expectedServices);
    }

    @Test
    public void servicesSpecialSize() {
        List<String> expectedServices = extract(getSpecialServicesList(), on(Service.class).getServiceName());
        List<String> actualServices =  new ArrayList<>();
        for (HtmlElement item : allServicesPage.allServicesSpecialList.items ) {
            String text = item.getText();
            text = text.split("\\n")[0];
            if (!text.equals("")) {
                actualServices.add(text);
            }
        }
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
