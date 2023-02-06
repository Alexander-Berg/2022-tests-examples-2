package ru.yandex.autotests.mordamobile.steps;

import org.openqa.selenium.WebDriver;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.mordamobile.blocks.all.AllServicesAllList;
import ru.yandex.autotests.mordamobile.blocks.all.AllServicesAllList.ServiceAllGroup;
import ru.yandex.autotests.mordamobile.blocks.all.AllServicesAllList.ServiceAllItem;
import ru.yandex.autotests.mordamobile.blocks.all.AllServicesTopList;
import ru.yandex.autotests.mordamobile.blocks.all.AllServicesTopList.ServiceTopItem;
import ru.yandex.autotests.mordamobile.pages.AllServicesPage;
import ru.yandex.autotests.mordamobile.utils.Service;
import ru.yandex.qatools.allure.annotations.Step;

import java.util.List;

import static org.hamcrest.Matchers.equalTo;
import static org.junit.Assert.assertThat;
import static org.junit.Assert.fail;
import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.HREF;
import static ru.yandex.autotests.mordamobile.data.AllServicesData.getExpectedAllOrder;

/**
 * User: Poluektov Evgeniy <poluektov@yandex-team.ru>
 * on: 05.02.2015.
 */
public class AllServicesSteps {
    private WebDriver driver;
    private AllServicesPage yandexComTrPage;

    public CommonMordaSteps userSteps;

    public AllServicesSteps(WebDriver driver) {
        this.driver = driver;
        userSteps = new CommonMordaSteps(driver);
        yandexComTrPage = new AllServicesPage(driver);
    }

    @Step
    public void shouldSeeService(AllServicesTopList allServicesTopList, Service serviceInfo) {
        ServiceTopItem service = findServiceTopList(allServicesTopList, serviceInfo);
        if (service != null) {
            userSteps.shouldSeeElement(service);

            userSteps.shouldSeeElement(service.serviceIcon);

            userSteps.shouldSeeElement(service.serviceName);
            userSteps.shouldSeeElementWithText(service.serviceName, serviceInfo.name);

            userSteps.shouldSeeElement(service.description);
            userSteps.shouldSeeElementWithText(service.description, serviceInfo.description);

            userSteps.shouldSeeElement(service.url);
            userSteps.shouldSeeElementMatchingTo(service.url, hasAttribute(HREF, serviceInfo.href));
        }
    }

    @Step
    public void shouldSeeService(AllServicesAllList allServicesAllList, Service serviceInfo) {
        ServiceAllItem service = findServiceInAllList(allServicesAllList, serviceInfo);
        if (service != null) {
            userSteps.shouldSeeElement(service);
            userSteps.shouldSeeElementWithText(service, serviceInfo.name);
            userSteps.shouldSeeElement(service.serviceIcon);
            userSteps.shouldSeeElement(service.href);
            userSteps.shouldSeeElementMatchingTo(service.href, hasAttribute(HREF, serviceInfo.href));
        }
    }

    @Step
    private ServiceAllItem findServiceInAllList(AllServicesAllList allServicesAllList, Service service) {
        for (ServiceAllGroup group : allServicesAllList.groups) {
            if (service.allGroup.matches(group.firstLetter.getText())) {
                for (ServiceAllItem item : group.items) {
                    if (service.name.matches(item.getText())) {
                        return item;
                    }
                }
            }
        }
        fail("Сервис " + service + " в рубрике " + allServicesAllList + " не найден");
        return null;
    }

    @Step
    public ServiceTopItem findServiceTopList(AllServicesTopList allServicesTopList, Service service) {
        for (ServiceTopItem item : allServicesTopList.items) {
            if (service.name.matches(item.serviceName.getText())) {
                return item;
            }
        }
        fail("Сервис " + service + " в рубрике " + allServicesTopList + " не найден");
        return null;
    }

    @Step
    public void shouldSeeServicesInOrder(List<String> services, List<String> sorted) {
        int i = 0;
        for (String service : services) {
            assertThat("На позиции " + (i + 1) + " неверный сервис", service, equalTo(sorted.get(i++)));
        }
    }
}
