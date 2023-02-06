package ru.yandex.autotests.morda.pages.touch.ru.blocks;

import org.hamcrest.Matcher;
import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validateable;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validator;
import ru.yandex.autotests.morda.pages.touch.ru.TouchRuMorda;
import ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector;
import ru.yandex.autotests.mordabackend.beans.topnews.TopnewsTab;
import ru.yandex.autotests.mordabackend.beans.topnews.TopnewsTabItem;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import java.util.List;

import static org.hamcrest.Matchers.*;
import static org.junit.Assert.assertThat;
import static ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector.collector;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElement;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElementMatchingTo;
import static ru.yandex.autotests.morda.steps.WebElementSteps.clickOn;
import static ru.yandex.autotests.morda.steps.WebElementSteps.shouldSee;
import static ru.yandex.autotests.morda.utils.matchers.AllOfDetailedMatcher.allOfDetailed;
import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.DATA_KEY;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.HREF;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;
import static ru.yandex.qatools.htmlelements.matchers.WrapsElementMatchers.hasText;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 19/05/15
 */
@Name("Блок Новостей")
@FindBy(xpath = "//div[contains(@class, 'content')]/div[contains(@class,'news')]")
public class NewsBlock extends HtmlElement implements Validateable<TouchRuMorda> {

    @Name("Категории новостей")
    @FindBy(xpath = ".//a[contains(@class, 'swiper__category')]")
    private List<HtmlElement> categories;

    @Name("Список новостей")
    @FindBy(xpath = ".//div[contains(@class, 'swiper__page') and not(contains(@class, 'swiper__page_visible_no'))]//a[not(contains(@class, 'news__item_type_promo'))]")
    private List<NewsItem> items;

    @Step("Set sport category")
    public void setSportCategory() {
        HtmlElement category = categories.stream()
                .filter(e -> "sport".equals(e.getAttribute("data-key")))
                .findFirst()
                .get();
        shouldSee(category);
        clickOn(category);
    }

    @Step("Should be selected sport category")
    public void shouldBeSelectedSportCategory(){
        String classAttribute = categories.stream()
                .filter(e -> "sport".equals(e.getAttribute("data-key")))
                .findFirst()
                .get()
                .getAttribute("class");

        assertThat("Category don't selected",
                classAttribute,
                containsString("swiper__category_selected_yes"));

    }

    @Override
    @Step("Check news")
    public HierarchicalErrorCollector validate(Validator<? extends TouchRuMorda> validator) {
        return collector()
                .check(shouldSeeElement(this))
                .check(
                        validateNewsCategories(validator),
                        validateItems(validator)
                );
    }

    @Step("Check news categories")
    public HierarchicalErrorCollector validateNewsCategories(Validator<? extends TouchRuMorda> validator) {
        HierarchicalErrorCollector collector = collector();

        for (int i = 0; i != Math.min(validator.getCleanvars().getTopnews().getTabs().size(), categories.size()); i++) {
            HtmlElement item = categories.get(i);
            TopnewsTab tab = validator.getCleanvars().getTopnews().getTabs().get(i);

            collector.check(validateNewsCategory(validator, item, tab));
        }

        HierarchicalErrorCollector categoriesCountCollector = collector().check(
                shouldSeeElementMatchingTo(categories,
                        hasSize(validator.getCleanvars().getTopnews().getTabs().size())
                ));

        collector.check(categoriesCountCollector);

        return collector;
    }

    @Step("Check category: {1}")
    public HierarchicalErrorCollector validateNewsCategory(Validator<? extends TouchRuMorda> validator,
                                                           HtmlElement category,
                                                           TopnewsTab tab
    ) {
        Matcher<String> tabText = tab.getKey().equals("index")
                ? equalTo(getTranslation("home", "mobile", "info_news.all", validator.getMorda().getLanguage()).toUpperCase())
                : equalTo(tab.getTitle().toUpperCase());

        return collector()
                .check(shouldSeeElement(category))
                .check(
                        shouldSeeElementMatchingTo(category, allOfDetailed(
                                hasText(tabText),
                                hasAttribute(HREF, equalTo(tab.getHref())),
                                hasAttribute(DATA_KEY, equalTo(tab.getKey()))
                        ))
                );
    }

    @Step("Check news items")
    public HierarchicalErrorCollector validateItems(Validator<? extends TouchRuMorda> validator) {
        HierarchicalErrorCollector collector = collector();

        //todo: check tv events in all tabs
        collector.check(validateNewsItems(validator, categories.get(0), validator.getCleanvars().getTopnews().getTabs().get(0)));

        return collector;
    }

    @Step("Check tab news items: {1}")
    public HierarchicalErrorCollector validateNewsItems(Validator<? extends TouchRuMorda> validator,
                                                        HtmlElement channel,
                                                        TopnewsTab tab
    ) {
        HierarchicalErrorCollector collector = collector();

        for (int i = 0; i != Math.min(tab.getNews().size(), items.size()); i++) {
            NewsItem item = items.get(i);
            TopnewsTabItem topnewsTabItem = tab.getNews().get(i);

            collector.check(validateNewsItem(validator, item, topnewsTabItem));
        }

        HierarchicalErrorCollector tvEventsCountCollector = collector().check(
                shouldSeeElementMatchingTo(items,
                        hasSize(tab.getNews().size())
                ));

        collector.check(tvEventsCountCollector);

        return collector;
    }

    @Step("Check tab news item: {1}")
    public HierarchicalErrorCollector validateNewsItem(Validator<? extends TouchRuMorda> validator,
                                                       NewsItem item,
                                                       TopnewsTabItem topnewsTabItem
    ) {
        return collector()
                .check(shouldSeeElement(item))
                .check(
                        collector()
                                .check(shouldSeeElementMatchingTo(item, allOfDetailed(
                                        hasAttribute(HREF, equalTo(topnewsTabItem.getHref())),
                                        hasText(topnewsTabItem.getText() + topnewsTabItem.getHreftext())
                                ))),
                        collector()
                                .check(shouldSeeElement(item.arrowIcon))
                );
    }

    public static class NewsItem extends HtmlElement {

        @Name("Стрелочка")
        @FindBy(xpath = ".//div[@class='listview__arrow']")
        private HtmlElement arrowIcon;

    }

}
