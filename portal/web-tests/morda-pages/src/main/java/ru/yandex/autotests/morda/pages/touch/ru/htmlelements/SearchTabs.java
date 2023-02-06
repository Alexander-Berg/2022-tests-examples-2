package ru.yandex.autotests.morda.pages.touch.ru.htmlelements;

import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validateable;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validator;
import ru.yandex.autotests.morda.pages.touch.ru.TouchRuMorda;
import ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector;
import ru.yandex.autotests.mordabackend.beans.servicestabs.ServicesTab;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import java.util.List;

import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.hasSize;
import static ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector.collector;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElement;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElementMatchingTo;
import static ru.yandex.autotests.morda.steps.CheckSteps.url;
import static ru.yandex.autotests.morda.utils.matchers.AllOfDetailedMatcher.allOfDetailed;
import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.HREF;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;
import static ru.yandex.qatools.htmlelements.matchers.WrapsElementMatchers.hasText;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 31/03/15
 */
@Name("Блок с поисковыми табами")
@FindBy(xpath = "//div[contains(@class, 'mtabs')]")
public class SearchTabs extends HtmlElement implements Validateable<TouchRuMorda> {

    @Name("Поисковые табы")
    @FindBy(xpath = ".//a[contains(@class, 'mtabs__item')]")
    private List<HtmlElement> searchTabs;

    @Override
    @Step("Check search tabs")
    public HierarchicalErrorCollector validate(Validator<? extends TouchRuMorda> validator) {

        HierarchicalErrorCollector collector = collector();
        List<ServicesTab> tabsData = validator.getCleanvars().getServicesTabs().getList();

        for (int i = 0; i != Math.min(tabsData.size(), searchTabs.size()); i++) {
            collector.check(validateSearchTab(searchTabs.get(i), tabsData.get(i), validator));
        }

        HierarchicalErrorCollector tabsCountCollector = collector().check(
                shouldSeeElementMatchingTo(searchTabs, hasSize(tabsData.size()))
        );

        collector.check(tabsCountCollector);

        return collector;
    }

    @Step("Check search tab: {0}")
    public HierarchicalErrorCollector validateSearchTab(HtmlElement tab, ServicesTab tabData, Validator<? extends TouchRuMorda> validator) {
        return collector()
                .check(shouldSeeElement(tab))
                .check(
                        shouldSeeElementMatchingTo(tab, allOfDetailed(
                                hasText(getTranslation("home", "services", "services." + tabData.getId() + ".title", validator.getMorda().getLanguage())),
                                hasAttribute(HREF, equalTo(url(tabData.getUrl(), validator.getMorda().getScheme())))
                        ))
                );
    }
}
