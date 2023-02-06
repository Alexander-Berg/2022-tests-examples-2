package ru.yandex.autotests.mainmorda.steps;

import org.junit.Assert;
import org.openqa.selenium.WebDriver;
import ru.yandex.autotests.mainmorda.blocks.all.AllServicesAllList;
import ru.yandex.autotests.mainmorda.blocks.all.AllServicesBottomList;
import ru.yandex.autotests.mainmorda.blocks.all.AllServicesSpecialList;
import ru.yandex.autotests.mainmorda.blocks.all.AllServicesTopList;
import ru.yandex.autotests.mainmorda.blocks.all.ServiceItem;
import ru.yandex.autotests.mainmorda.pages.AllServicesPage;
import ru.yandex.autotests.mainmorda.utils.Service;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.qatools.allure.annotations.Step;

import java.util.List;

import static org.hamcrest.Matchers.equalTo;
import static org.junit.Assert.fail;
import static ru.yandex.autotests.mainmorda.blocks.all.AllServicesAllList.*;
import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.HREF;

/**
 * User: alex89
 * Date: 30.10.12
 */
public class AllServicesSteps {
    private WebDriver driver;
    private AllServicesPage mainPage;

    public CommonMordaSteps userSteps;

    public AllServicesSteps(WebDriver driver) {
        this.driver = driver;
        userSteps = new CommonMordaSteps(driver);
        mainPage = new AllServicesPage(driver);
    }

    @Step
    public void shouldSeeService(AllServicesTopList allServicesTopList, Service serviceInfo) {
        ServiceItem service = findServiceTopList(allServicesTopList, serviceInfo);
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
    public void shouldSeeService(AllServicesBottomList allServicesBottomList, Service serviceInfo) {
        ServiceItem service = findServiceBottomList(allServicesBottomList, serviceInfo);
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
    public void shouldSeeService(AllServicesSpecialList allServicesSpecialList, Service serviceInfo) {
        ServiceItem service = findServiceSpecialList(allServicesSpecialList, serviceInfo);
        if (service != null) {
            userSteps.shouldSeeElement(service);

            userSteps.shouldSeeElement(service.serviceIcon);

            userSteps.shouldSeeElement(service.serviceName);
            userSteps.shouldSeeElementWithText(service.serviceName, serviceInfo.name);

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
    public ServiceItem findServiceTopList(AllServicesTopList allServicesTopList, Service service) {
        for (ServiceItem item : allServicesTopList.items) {
            if (service.name.matches(item.serviceName.getText())) {
                return item;
            }
        }
        fail("Сервис " + service + " в рубрике " + allServicesTopList + " не найден");
        return null;
    }

    @Step
    public ServiceItem findServiceBottomList(AllServicesBottomList allServicesBottomList, Service service) {
        for (ServiceItem item : allServicesBottomList.items) {
            if (service.name.matches(item.serviceName.getText())) {
                return item;
            }
        }
        fail("Сервис " + service + " в рубрике " + allServicesBottomList + " не найден");
        return null;
    }

    @Step
    public ServiceItem findServiceSpecialList(AllServicesSpecialList allServicesSpecialList, Service service) {
        for (ServiceItem item : allServicesSpecialList.items) {
            if (service.name.matches(item.serviceName.getText())) {
                return item;
            }
        }
        fail("Сервис " + service + " в рубрике " + allServicesSpecialList + " не найден");
        return null;
    }

    @Step
    public void shouldSeeServicesInOrder(List<String> services, List<String> sorted) {
        int i = 0;
        for (String service : services) {
            Assert.assertThat("На позиции " + (i + 1) + " неверный сервис", service, equalTo(sorted.get(i++)));
        }
    }
}

