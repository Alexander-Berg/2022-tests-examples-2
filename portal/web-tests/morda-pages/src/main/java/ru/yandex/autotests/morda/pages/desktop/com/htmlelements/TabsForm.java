package ru.yandex.autotests.morda.pages.desktop.com.htmlelements;

import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.morda.pages.desktop.com.DesktopComMorda;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validateable;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validator;
import ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector;
import ru.yandex.autotests.mordabackend.beans.servicestabs.ServicesTab;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import java.util.List;

import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.hasSize;
import static org.hamcrest.Matchers.startsWith;
import static ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector.collector;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElement;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElementMatchingTo;
import static ru.yandex.autotests.morda.steps.CheckSteps.url;
import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.CLASS;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.HREF;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;
import static ru.yandex.qatools.htmlelements.matchers.WrapsElementMatchers.hasText;

/**
 * User: asamar
 * Date: 29.09.2015.
 */
@Name("Блок табов")
@FindBy(xpath = "//div[@class='tabs']")
public class TabsForm extends HtmlElement implements Validateable<DesktopComMorda> {

    @Name("Список табов")
    @FindBy(xpath = ".//a")
    public List<Tab> tabs;

    public static class Tab extends HtmlElement {

        @Name("Иконка svg")
        @FindBy(xpath = "./div[contains(@class, 'tabs__item-image')]")
        public HtmlElement icon;

        @Name("Подпись иконки")
        @FindBy(xpath = "./div[contains(@class, 'tabs__item-text')]")
        public HtmlElement tabText;
    }

    @Override
    public HierarchicalErrorCollector validate(Validator<? extends DesktopComMorda> validator) {

        List<ServicesTab> servicesTabs = validator.getCleanvars().getServicesTabs().getList();

        HierarchicalErrorCollector collector = collector();
        collector.check(shouldSeeElement(this));

        for (int i = 0; i < Math.min(tabs.size(), servicesTabs.size()); i++) {
            collector.check(validateTab(tabs.get(i), servicesTabs.get(i), validator));
        }

        HierarchicalErrorCollector countCollector = collector().check(
                shouldSeeElementMatchingTo(tabs, hasSize(servicesTabs.size()))
        );
        collector.check(countCollector);

        return collector;
    }

    public static HierarchicalErrorCollector validateTab(Tab tab,
                                                         ServicesTab servicesTab,
                                                         Validator<? extends DesktopComMorda> validator) {
        return collector()
                .check(shouldSeeElement(tab))
                .check(
                        shouldSeeElementMatchingTo(tab, hasAttribute(
                                HREF, startsWith(url(servicesTab.getUrl(), "https")))),//startWith, потому что '/'
                        shouldSeeElementMatchingTo(tab.tabText, hasText(

                                        getTranslation(
                                                "home",
                                                "spok_yes",
                                                "tabs." + servicesTab.getId(),
                                                validator.getMorda().getLanguage())
                                )
                        ),
                        shouldSeeElementMatchingTo(tab.icon, hasAttribute(
                                CLASS, equalTo("tabs__item-image tabs__" + servicesTab.getId())))
                );
    }

    public List<Tab> getTabs() {
        return tabs;
    }
}
