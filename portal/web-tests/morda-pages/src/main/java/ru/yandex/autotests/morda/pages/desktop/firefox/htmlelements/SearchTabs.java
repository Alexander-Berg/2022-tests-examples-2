package ru.yandex.autotests.morda.pages.desktop.firefox.htmlelements;

import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.morda.pages.desktop.firefox.DesktopFirefoxMorda;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validateable;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validator;
import ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector;
import ru.yandex.autotests.mordabackend.beans.servicestabs.ServicesTab;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import java.util.List;
import java.util.stream.Collectors;

import static org.hamcrest.Matchers.hasSize;
import static org.hamcrest.Matchers.startsWith;
import static ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector.collector;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElement;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElementMatchingTo;
import static ru.yandex.autotests.morda.utils.matchers.AllOfDetailedMatcher.allOfDetailed;
import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.HREF;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;
import static ru.yandex.qatools.htmlelements.matchers.WrapsElementMatchers.hasText;

/**
 * User: asamar
 * Date: 26.08.2015.
 */
@Name("Поисковые табы")
@FindBy(xpath = "//div[contains(@class, 'tabs')]")
public class SearchTabs extends HtmlElement implements Validateable<DesktopFirefoxMorda> {

    private SearchForm searchForm;

    @Name("Поисковые табы")
    @FindBy(xpath = ".//a")
    private List<HtmlElement> searchTabs;

    @Override
    @Step("Check search tabs")
    public HierarchicalErrorCollector validate(Validator<? extends DesktopFirefoxMorda> validator) {

        HierarchicalErrorCollector collector = collector();
        List<SearchTabInfo> expectedTabs = getSearchTabs(validator);

        for (int i = 0; i != Math.min(expectedTabs.size(), searchTabs.size()); i++) {
            collector.check(validateSearchTab(searchTabs.get(i), expectedTabs.get(i)));
        }

        HierarchicalErrorCollector tabsCountCollector = collector().check(
                shouldSeeElementMatchingTo(searchTabs, hasSize(expectedTabs.size()))
        );

        collector.check(tabsCountCollector);

        return collector;
    }

    @Step("Check search tab: {1}")
    public HierarchicalErrorCollector validateSearchTab(HtmlElement tab, SearchTabInfo info) {
        return collector()
                .check(shouldSeeElement(tab))
                .check(
                        shouldSeeElementMatchingTo(tab, allOfDetailed(
                                        hasText(info.text),
                                        hasAttribute(HREF, startsWith(info.href))
                                )
                        )
                );
    }

    private String normalize(String scheme, String url) {
        if (url.startsWith("//")) {
            return scheme + ":" + url;
        }
        return url;
    }

    public List<SearchTabInfo> getSearchTabs(Validator<? extends DesktopFirefoxMorda> validator) {
        List<ServicesTab> cleanvarsTabs = validator.getCleanvars().getServicesTabs().getList();

        return cleanvarsTabs.stream()
                .map(
                        tab -> new SearchTabInfo(
                                tab.getId(),
                                getTranslation("home", "tabs", tab.getId(), validator.getMorda().getLanguage()),
                                normalize(validator.getMorda().getScheme(), tab.getUrl())
                        )
                ).collect(Collectors.toList());
    }

    public static class SearchTabInfo {
        public String id;
        public String text;
        public String href;

        public SearchTabInfo(String id, String text, String href) {
            this.id = id;
            this.text = text;
            this.href = href;
        }

        @Override
        public String toString() {
            return id;
        }
    }


}
