package ru.yandex.autotests.morda.pages.touch.ru.blocks;

import org.hamcrest.Matchers;
import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validateable;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validator;
import ru.yandex.autotests.morda.pages.touch.ru.TouchRuMorda;
import ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector;
import ru.yandex.autotests.morda.utils.matchers.AllOfDetailedMatcher;
import ru.yandex.autotests.mordabackend.beans.collections.Item;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import java.util.List;

import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.hasSize;
import static ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector.collector;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElement;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElementMatchingTo;
import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.DATA_IMAGE;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.HREF;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslationSafely;
import static ru.yandex.qatools.htmlelements.matchers.common.HasTextMatcher.hasText;

/**
 * User: asamar
 * Date: 16.02.17
 */
@Name("Блок коллекций")
@FindBy(xpath = "//div[contains(@class, 'collections ')]")
public class CollectionsBlock extends HtmlElement implements Validateable<TouchRuMorda> {

    @Name("Заголовок")
    @FindBy(xpath = ".//a[contains(@class, 'collections__title')]")
    private HtmlElement collectionsTitle;

    @Name("Список коллекций")
    @FindBy(xpath = ".//a[contains(@class, 'collections__item')]")
    private List<CollectionTile> collectionsItems;

    @Step("Validate collections")
    @Override
    public HierarchicalErrorCollector validate(Validator<? extends TouchRuMorda> validator) {
        return collector()
                .check(validateTitle(collectionsTitle, validator))
                .check(validateItems(collectionsItems, validator));
    }

    @Step("{0}")
    public HierarchicalErrorCollector validateTitle(HtmlElement title, Validator<? extends TouchRuMorda> validator) {
        return collector()
                .check(shouldSeeElement(title))
                .check(shouldSeeElementMatchingTo(title, AllOfDetailedMatcher.allOfDetailed(
                        hasText(getTranslationSafely("home", "api_search", "collections.title", validator.getMorda().getLanguage())),
                        hasAttribute(HREF, equalTo("https://collections.yandex.ru/"))
                )));
    }

    @Step("{0}")
    private HierarchicalErrorCollector validateItems(List<CollectionTile> items, Validator<? extends TouchRuMorda> validator) {
        HierarchicalErrorCollector collector = collector();

        List<Item> cleanvarsItems = validator.getCleanvars().getCollections().getList();

        for (int i = 0; i != Math.min(cleanvarsItems.size(), items.size()); i++) {

            Item collectionItem = cleanvarsItems.get(i);

            collector.check(validateItem(items.get(i), collectionItem, validator));
        }

        HierarchicalErrorCollector collectionsCountCollector = collector().check(
                shouldSeeElementMatchingTo(items,
                        hasSize(validator.getCleanvars().getCollections().getList().size())
                ));

        collector.check(collectionsCountCollector);

        return collector;
    }

    @Step("{0}")
    private HierarchicalErrorCollector validateItem(CollectionTile tile,
                                                    Item item,
                                                    Validator<? extends TouchRuMorda> validator) {

        String link = item.getLink();
        String title = item.getTitle().replaceAll(" ", " ");//неразрывный пробел, видимо

        return collector()
                .check(shouldSeeElement(tile))
                .check(
                        collector()
                                .check(shouldSeeElementMatchingTo(tile, hasAttribute(HREF, equalTo(link)))),
                        collector()
                                .check(shouldSeeElement(tile.collectionsTitle))
                                .check(shouldSeeElementMatchingTo(tile.collectionsTitle, hasText(title))),
                        collector()
                                .check(shouldSeeElement(tile.img))
                                .check(shouldSeeElementMatchingTo(tile.img, hasAttribute(DATA_IMAGE,
                                        Matchers.startsWith("//home.yastatic.net/morda-logo/i/collections/"))))
                );
    }

    public static class CollectionTile extends HtmlElement {

        @Name("Картинка")
        @FindBy(xpath = ".//div[contains(@class, 'collections__item-img')]")
        private HtmlElement img;

        @Name("Заголовок")
        @FindBy(xpath = ".//div[@class = 'collections__item-title']")
        private HtmlElement collectionsTitle;

    }

}
