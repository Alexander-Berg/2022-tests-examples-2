package ru.yandex.autotests.morda.pages.desktop.main.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.morda.pages.desktop.main.DesktopMainMorda;
import ru.yandex.autotests.morda.pages.desktop.main.htmlelements.Widget;
import ru.yandex.autotests.morda.pages.desktop.mainall.DesktopMainAllMorda;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validateable;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validator;
import ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector;
import ru.yandex.autotests.mordabackend.beans.servicesblock.ServicesBlockLink;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import java.util.List;

import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.hasSize;
import static ru.yandex.autotests.morda.pages.desktop.main.blocks.ServicesBlock.ServicesItem.validateServiceItem;
import static ru.yandex.autotests.morda.pages.desktop.mainall.DesktopMainAllMorda.desktopMainAll;
import static ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector.collector;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElement;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElementMatchingTo;
import static ru.yandex.autotests.morda.steps.CheckSteps.url;
import static ru.yandex.autotests.morda.utils.matchers.AllOfDetailedMatcher.allOfDetailed;
import static ru.yandex.autotests.morda.utils.matchers.UrlMatcher.urlMatcher;
import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.HREF;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.A11y.POPULAR;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;
import static ru.yandex.qatools.htmlelements.matchers.WrapsElementMatchers.hasText;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 01/04/15
 */
@Name("Посещаемое")
@FindBy(xpath = "//div[contains(@id, 'wd-wrapper-_services')]")
public class ServicesBlock extends Widget<ServicesSettingsBlock> implements Validateable<DesktopMainMorda> {

    @Name("Заголовок")
    @FindBy(xpath = ".//h1//a")
    public HtmlElement title;

    @Name("Основные сылки на сервисы")
    @FindBy(xpath = ".//ul[@class='list']//li")
    public List<ServicesItem> serviceItems;

    @Name("Все сылки на сервисы")
    @FindBy(xpath = ".//a[contains(@class, 'link_bold_yes')]")
    public List<HtmlElement> additionalServiceItems;

    public ServicesSettingsBlock servicesSettingsBlock;

    @Override
    public ServicesSettingsBlock getSetupPopup(){
        return servicesSettingsBlock;
    }

    @Step("{0}")
    public static HierarchicalErrorCollector validateTitle(HtmlElement title,
                                                           Validator<? extends DesktopMainMorda> validator) {

        DesktopMainMorda morda = validator.getMorda();
        String env = validator.getMorda().getEnvironment().getEnvironment();
        DesktopMainAllMorda mordaAll = desktopMainAll(morda.getScheme(), env, morda.getRegion());

        return collector()
                .check(shouldSeeElement(title))
                .check(
                        shouldSeeElementMatchingTo(title, allOfDetailed(
                                hasText(getTranslation(POPULAR, validator.getMorda().getLanguage())),
                                hasAttribute(HREF, equalTo(mordaAll.getUrl().toString()))
                        ))
                );
    }

    @Step("{0}")
    public static HierarchicalErrorCollector validateServiceItems(List<ServicesItem> serviceItems,
                                                                  Validator<? extends DesktopMainMorda> validator) {
        List<ServicesBlockLink> serviceItemsData = validator.getCleanvars().getServices().getHash().get("2");

        HierarchicalErrorCollector collector = collector();

        for (int i = 0; i != Math.min(serviceItemsData.size(), serviceItems.size()); i++) {
            collector.check(validateServiceItem(serviceItems.get(i), serviceItemsData.get(i), validator));
        }

        HierarchicalErrorCollector countCollector = collector().check(
                shouldSeeElementMatchingTo(serviceItems, hasSize(serviceItemsData.size()))
        );
        collector.check(countCollector);

        return collector;
    }

    @Override
    @Step("Check services block")
    public HierarchicalErrorCollector validate(Validator<? extends DesktopMainMorda> validator) {
        return collector()
                .check(shouldSeeElement(this))
                .check(
                        validateTitle(title, validator),
                        validateServiceItems(serviceItems, validator)
                );
    }

    public static class ServicesItem extends HtmlElement {

        @Name("Ссылка на сервис")
        @FindBy(xpath = ".//a[1]")
        public HtmlElement service;

        @Name("Подпись")
        @FindBy(xpath = ".//a[2]")
        public HtmlElement text;

        @Name("Разделитель")
        @FindBy(xpath = ".//span")
        public HtmlElement delimeter;

        @Step("{0}")
        public static HierarchicalErrorCollector validateService(HtmlElement service,
                                                                 ServicesBlockLink serviceData,
                                                                 Validator<? extends DesktopMainMorda> validator) {

            return collector()
                    .check(shouldSeeElement(service))
                    .check(
                            shouldSeeElementMatchingTo(service, allOfDetailed(
                                    hasText(getTranslation("home", "services", "services." + serviceData.getId() + ".title", validator.getMorda().getLanguage())),
                                    hasAttribute(HREF, urlMatcher(
                                            url(serviceData.getUrl(), validator.getMorda().getScheme())).build())
                            ))
                    );
        }

        @Step("{0}")
        public static HierarchicalErrorCollector validateDelimiter(HtmlElement delimiter,
                                                                   ServicesBlockLink serviceData,
                                                                   Validator<? extends DesktopMainMorda> validator) {

            return collector()
                    .check(shouldSeeElement(delimiter))
                    .check(
                            shouldSeeElementMatchingTo(delimiter, hasText(" — "))
                    );
        }

        @Step("{0}")
        public static HierarchicalErrorCollector validateText(HtmlElement text,
                                                              ServicesBlockLink serviceData,
                                                              Validator<? extends DesktopMainMorda> validator) {

            return collector()
                    .check(shouldSeeElement(text))
                    .check(
                            shouldSeeElementMatchingTo(text, allOfDetailed(
                                    hasText(serviceData.getText().replace(" ", " ")),
                                    hasAttribute(HREF, equalTo(url(serviceData.getUrltext(), validator.getMorda().getScheme())))
                            ))
                    );
        }

        @Step("{0}")
        public static HierarchicalErrorCollector validateServiceItem(ServicesItem serviceItem,
                                                                     ServicesBlockLink serviceData,
                                                                     Validator<? extends DesktopMainMorda> validator) {
            return collector()
                    .check(shouldSeeElement(serviceItem))
                    .check(
                            validateService(serviceItem.service, serviceData, validator),
                            validateDelimiter(serviceItem.delimeter, serviceData, validator),
                            validateText(serviceItem.text, serviceData, validator)
                    );
        }
    }
}
