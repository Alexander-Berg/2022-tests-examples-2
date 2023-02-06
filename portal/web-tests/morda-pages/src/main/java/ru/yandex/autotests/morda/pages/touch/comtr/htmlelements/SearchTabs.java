package ru.yandex.autotests.morda.pages.touch.comtr.htmlelements;

import org.hamcrest.Matcher;
import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.morda.pages.interfaces.blocks.BlockWithTabs;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validateable;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validator;
import ru.yandex.autotests.morda.pages.touch.comtr.TouchComTrMorda;
import ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector;
import ru.yandex.autotests.mordacommonsteps.utils.TextInput;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.autotests.utils.morda.language.TankerManager;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import java.util.ArrayList;
import java.util.List;

import static org.hamcrest.Matchers.containsString;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.startsWith;
import static ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector.collector;
import static ru.yandex.autotests.morda.utils.matchers.AllOfDetailedMatcher.allOfDetailed;
import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.autotests.mordacommonsteps.matchers.RegexMatcher.matches;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.CLASS;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.HREF;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Mobile.MAIL_TITLE;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Mobile.TAB_IMAGES;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Mobile.TAB_TRANSLATE;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Mobile.TAB_VIDEO;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;
import static ru.yandex.qatools.htmlelements.matchers.WrapsElementMatchers.hasText;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 31/03/15
 */
@Name("Поисковые информеры")
@FindBy(xpath = "//div[contains(@class, 'content__informers')]")
public class SearchTabs extends HtmlElement implements BlockWithTabs<SearchTab>, Validateable<TouchComTrMorda> {

    @Name("Поисковый информер")
    @FindBy(xpath = ".//a[contains(@class, 'informers__cell')]")
    private List<SearchTab> searchTabs;

    private SearchForm searchForm;

    @Override
    @Step("Check search informers")
    public HierarchicalErrorCollector validate(Validator<? extends TouchComTrMorda> validator) {
        List<SearchTabMatcher> tabMatchers = getTabMatchers(validator);
        HierarchicalErrorCollector collector = collector();

        for (int i = 0; i != Math.min(tabMatchers.size(), searchTabs.size()); i++) {
            collector.check(checkTab(searchTabs.get(i), tabMatchers.get(i)));
        }
//        steps.shouldSeeListWithSize(searchTabs, equalTo(tabMatchers.size()));

        return collector;
    }

    @Step("Check {0}: {1}")
    public HierarchicalErrorCollector checkTab(SearchTab tab, SearchTabMatcher matcher) {
        return tab.checkTab(matcher);
    }

    @Override
    public List<? extends SearchTab> getSearchTabs() {
        return searchTabs;
    }

    @Override
    public TextInput getSearchInput() {
        return searchForm.getSearchInput();
    }

    @Override
    public HtmlElement getSearchButton() {
        return searchForm.getSearchButton();
    }

    @Override
    public HtmlElement getLr() {
        return searchForm.getLr();
    }

    public List<SearchTabMatcher> getTabMatchers(Validator<? extends TouchComTrMorda> validator) {
        List<SearchTabMatcher> matchers = new ArrayList<>();
        TouchComTrMorda morda = validator.getMorda();

        matchers.add(new SearchTabMatcher(
                "traffic",
                allOfDetailed(
                        hasAttribute(CLASS, containsString("informers__icon__traffic")),
                        hasText(matches("[↑|↓]?"))
                ),
                hasText(matches("[0-9]|10")),
                hasAttribute(HREF, startsWith("https://yandex.com.tr/harita"))
        ));

        matchers.add(new SearchTabMatcher(
                "weather",
                hasAttribute(CLASS, containsString("informers__icon__weather")),
                hasText(matches("(0|(−?[1-9]\\d?))")),
                hasAttribute(HREF, startsWith("https://yandex.com.tr/hava"))
        ));

        matchers.add(new SearchTabMatcher(
                "stocks usd",
                allOfDetailed(
                        hasAttribute(CLASS, containsString("informers__icon__stocks")),
                        hasAttribute(CLASS, containsString("informers__icon__dollar")),
                        hasText(matches("[↑|↓]?"))
                ),
                hasText(matches("\\d+,\\d{2}[↑|↓]?")),
                hasAttribute(HREF, startsWith(morda.getScheme() + "://www.yandex.com.tr/search/touch/?text=usd%20d%C3%B6viz%20kuru"))
        ));

        matchers.add(new SearchTabMatcher(
                "stocks euro",
                allOfDetailed(
                        hasAttribute(CLASS, containsString("informers__icon__stocks")),
                        hasAttribute(CLASS, containsString("informers__icon__euro")),
                        hasText(matches("[↑|↓]?"))
                ),
                hasText(matches("\\d+,\\d{2}[↑|↓]?")),
                hasAttribute(HREF, startsWith(morda.getScheme() + "://www.yandex.com.tr/search/touch/?text=eur%20d%C3%B6viz%20kuru"))
        ));

        matchers.add(new SearchTabMatcher(
                "mail",
                hasAttribute(CLASS, containsString("informers__icon__mail")),
                hasText(equalTo(getTranslation(MAIL_TITLE, Language.TR))),
                hasAttribute(HREF, startsWith("https://mail.yandex.com.tr/"))
        ));

        matchers.add(new SearchTabMatcher(
                "images",
                hasAttribute(CLASS, containsString("informers__services__images")),
                hasText(equalTo(getTranslation(TAB_IMAGES, Language.TR))),
                hasAttribute(HREF, startsWith(morda.getScheme() + "://yandex.com.tr/gorsel/"))
        ));

        matchers.add(new SearchTabMatcher(
                "translate",
                hasAttribute(CLASS, containsString("informers__services__translate")),
                hasText(equalTo(getTranslation(TAB_TRANSLATE, Language.TR))),
                hasAttribute(HREF, startsWith(morda.getScheme() + "://ceviri.yandex.com.tr/m/translate"))
        ));

        matchers.add(new SearchTabMatcher(
                "video",
                hasAttribute(CLASS, containsString("informers__services__video")),
                hasText(equalTo(getTranslation(TankerManager.TRIM, TAB_VIDEO, Language.TR))),
                hasAttribute(HREF, startsWith(morda.getScheme() + "://yandex.com.tr/video/touch/"))
        ));

        return matchers;
    }

    public static class SearchTabMatcher {
        private String tab;
        private Matcher<? super HtmlElement> iconMatcher;
        private Matcher<? super HtmlElement> textMatcher;
        private Matcher<? super HtmlElement> hrefMatcher;

        public SearchTabMatcher(String tab, Matcher<? super HtmlElement> iconMatcher,
                                Matcher<? super HtmlElement> textMatcher, Matcher<? super HtmlElement> hrefMatcher) {
            this.tab = tab;
            this.iconMatcher = iconMatcher;
            this.textMatcher = textMatcher;
            this.hrefMatcher = hrefMatcher;
        }

        public Matcher<? super HtmlElement> getIconMatcher() {
            return iconMatcher;
        }

        public Matcher<? super HtmlElement> getTextMatcher() {
            return textMatcher;
        }

        public Matcher<? super HtmlElement> getHrefMatcher() {
            return hrefMatcher;
        }

        @Override
        public String toString() {
            return tab;
        }
    }
}
