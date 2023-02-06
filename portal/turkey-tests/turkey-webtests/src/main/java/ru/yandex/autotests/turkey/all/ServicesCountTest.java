package ru.yandex.autotests.turkey.all;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.turkey.Properties;
import ru.yandex.autotests.turkey.blocks.all.AllServicesAllList;
import ru.yandex.autotests.turkey.pages.AllServicesPage;
import ru.yandex.autotests.turkey.utils.Service;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import java.util.ArrayList;
import java.util.List;

import static ch.lambdaj.Lambda.extract;
import static ch.lambdaj.Lambda.on;
import static ru.yandex.autotests.turkey.data.AllServicesData.getAllServicesList;
import static ru.yandex.autotests.turkey.data.AllServicesData.getBottomServicesList;
import static ru.yandex.autotests.turkey.data.AllServicesData.getSpecialServicesList;
import static ru.yandex.autotests.turkey.data.AllServicesData.getTopServicesList;

/**
 * User: Poluektov Evgeniy <poluektov@yandex-team.ru>
 * on: 26.02.2015.
 */
@Aqua.Test(title = "Проверка кол-ва сервисов")
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
                on(AllServicesAllList.ServiceAllItem.class).getText());
        user.shouldSeeItemsInList(actualServices, expectedServices);
    }
}
