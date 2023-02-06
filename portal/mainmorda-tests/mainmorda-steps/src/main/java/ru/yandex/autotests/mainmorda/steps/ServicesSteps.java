package ru.yandex.autotests.mainmorda.steps;

import org.hamcrest.Matcher;
import org.openqa.selenium.WebDriver;
import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.mainmorda.pages.BasePage;
import ru.yandex.autotests.mainmorda.pages.MainPage;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.mordaexportsclient.beans.ServicesV122Entry;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import java.net.URI;
import java.util.List;

import static org.hamcrest.CoreMatchers.equalTo;
import static org.hamcrest.CoreMatchers.startsWith;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.not;
import static org.hamcrest.text.IsEmptyString.isEmptyOrNullString;
import static org.junit.Assert.fail;
import static ru.yandex.autotests.mainmorda.blocks.ServicesBlock.HtmlLinkWithComment;
import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.HREF;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;


/**
 * User: eoff
 * Date: 28.01.13
 */
public class ServicesSteps {
    private static final Properties CONFIG = new Properties();

    private WebDriver driver;
    private CommonMordaSteps userSteps;
    private BasePage basePage;
    private MainPage mainPage;
    private LinksSteps userLink;

    public ServicesSteps(WebDriver driver) {
        this.driver = driver;
        this.userSteps = new CommonMordaSteps(driver);
        this.basePage = new BasePage(driver);
        this.mainPage = new MainPage(driver);
        this.userLink = new LinksSteps(driver);
    }

    @Step
    public void shouldSeeServicesTitle(Matcher<String> title) {
        String allText = userSteps.getElementText(mainPage.servicesSettings.servicesTitle);
        assertThat("Неверный title сервисов", allText.substring(0, allText.indexOf("\n")), title);
    }

    @Step
    public void shouldSeeService(String service) {
        String serviceText = userSteps.getElementText(basePage.servicesBlock.allServices
                .get(0));
        assertThat("Неверное название сервиса", serviceText, equalTo(service));
    }

    private Matcher<String> getServiceHrefMatcher(ServicesV122Entry service) {
        String href = service.getHref().startsWith("//")
                ? CONFIG.getProtocol() + ":" + service.getHref()
                : service.getHref();
        href = href.replace("probki", "maps");
        URI uri = URI.create(href);
        return startsWith(uri.getScheme() + "://" + uri.getHost());
    }

    @Step
    public void shouldSeeServiceWithComment(ServicesV122Entry service) {
        HtmlLinkWithComment element = findServiceOnPage(service.getId());

        userSteps.shouldSeeElement(element);
        userSteps.shouldSeeElement(element.serviceLink);
        userSteps.shouldSeeElementMatchingTo(element.serviceLink, hasAttribute(HREF,
                getServiceHrefMatcher(service)));
        userSteps.shouldSeeElement(element.serviceComment);
        userSteps.shouldSeeElementWithText(element.serviceComment, not(isEmptyOrNullString()));
        userSteps.shouldSeeElementMatchingTo(element.serviceComment, hasAttribute(HREF,
                getServiceHrefMatcher(service)));
    }

    @Step
    public void shouldSeeServiceWithOutComment(ServicesV122Entry service) {
        HtmlElement element = findServiceOnPage(basePage.servicesBlock.serviceLinksWithoutComments,
                service.getId());
        shouldSeeServiceWithOutComment(element, service);
    }

    @Step
    public void shouldSeeServiceWithOutComment(HtmlElement serviceElement, ServicesV122Entry service) {
        URI uri = URI.create(service.getHref());
        userSteps.shouldSeeElement(serviceElement);
        userSteps.shouldSeeElementMatchingTo(serviceElement, hasAttribute(HREF,
                getServiceHrefMatcher(service)));
    }

    @Step
    public HtmlElement findServiceOnPage(List<HtmlElement> list, String id) {
        HtmlElement element = findServiceOnPageSafely(list, id);
        if (element != null) {
            return element;
        }
        fail("Не нашли сервиса на странице");
        return null;
    }

    @Step
    public HtmlElement findServiceOnPageSafely(List<HtmlElement> list, String id) {
        String text = getTranslation("home", "services", "services." + id + ".title", CONFIG.getLang());
        for (HtmlElement element : list) {
            if (text.equals(element.getText())) {
                return element;
            }
        }
        return null;
    }

    @Step
    public HtmlLinkWithComment findServiceOnPage(String id) {
        HtmlLinkWithComment result = findServiceOnPageSafely(id);
        if (result != null) {
            return result;
        }
        fail("Не нашли сервиса на странице");
        return null;
    }

    @Step
    public HtmlLinkWithComment findServiceOnPageSafely(String id) {
        String text = getTranslation("home", "services", "services." + id + ".title", CONFIG.getLang());
        for (HtmlLinkWithComment element : basePage.servicesBlock.serviceLinksWithComments) {
            if (text.equals(element.serviceLink.getText())) {
                return element;
            }
        }
        return null;
    }
}
