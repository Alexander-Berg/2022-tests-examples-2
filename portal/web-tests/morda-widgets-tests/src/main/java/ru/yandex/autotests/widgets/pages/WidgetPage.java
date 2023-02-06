package ru.yandex.autotests.widgets.pages;

import org.openqa.selenium.WebDriver;
import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.mordacommonsteps.utils.TextInput;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;
import ru.yandex.qatools.htmlelements.loader.HtmlElementLoader;

import java.util.List;

import static org.hamcrest.Matchers.containsString;
import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.CLASS;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 23.07.13
 */
public class WidgetPage {
    public WidgetPage(WebDriver driver) {
        HtmlElementLoader.populate(this, driver);
    }

    @Name("Региональные категории")
    @FindBy(xpath = "//ul[@class='b-categories']/li//a[contains(@href, '?region')]")
    public List<HtmlElement> regionalCategories;

    @Name("Общие категории")
    @FindBy(xpath = "//ul[@class='b-categories']/li//a[not(contains(@href, '?region'))]")
    public List<HtmlElement> commonCategories;

    @Name("Все категории")
    @FindBy(xpath = "//ul[@class='b-categories']/li")
    public List<CategoryElement> allCategories;

    @Name("Все тэги")
    @FindBy(xpath = "//div[@class='b-widget-tags']//self::node()[contains(@class, 'b-widget-tags__tag')]")
    public List<TagElement> allTags;

    @Name("Все виджеты")
    @FindBy(xpath = "//div[@class='b-catalog-widget']")
    public List<HtmlElement> allWidgets;

    @Name("Все ссылки виджетов")
    @FindBy(xpath = "//div[contains(@class, 'b-catalog-widget__link')]//a")
    public List<HtmlElement> allWidgetLinks;

    @Name("Все адреса виджетов")
    @FindBy(xpath = "//span[@class='b-catalog-widget__url']")
    public List<HtmlElement> allWidgetUrls;

    @Name("Регионы виджетов")
    @FindBy(xpath = "//div[@class='b-catalog-widget__regions']/a[@class='b-catalog-widget__region']")
    public List<HtmlElement> allRegions;

    @Name("Заголовок")
    @FindBy(xpath = "//h1[@class='b-page-title__title']")
    public HtmlElement title;

    @Name("Количество виджетов")
    @FindBy(xpath = "//span[@class='b-page-title__amount']")
    public HtmlElement widgetsAmount;

    @Name("Ссылка 'Следующая страница'")
    @FindBy(xpath = "//div[contains(@class,'b-pager')]//a[@class='b-pager__next']")
    public HtmlElement nextPageButton;

    @Name("Поле поиска")
    @FindBy(xpath = "//td[@class='b-search__input']//input[@class='b-form-input__input']")
    public TextInput searchField;

    @Name("Кнопка поиска")
    @FindBy(xpath = "//button[contains(@class, 'b-search__submit')]")
    public HtmlElement searchButton;

    public static class CategoryElement extends HtmlElement {
        @Name("Ссылка категории")
        @FindBy(xpath = ".//a")
        public HtmlElement link;

        @Override
        public boolean isSelected() {
            return hasAttribute(CLASS, containsString("b-categories__category_state_current")).matches(this);
        }

        @Override
        public void click() {
            link.click();
        }
    }

    public static class TagElement extends HtmlElement {
        @Override
        public boolean isSelected() {
            return hasAttribute(CLASS, containsString("b-widget-tags__tag_selected")).matches(this);
        }
    }
}
