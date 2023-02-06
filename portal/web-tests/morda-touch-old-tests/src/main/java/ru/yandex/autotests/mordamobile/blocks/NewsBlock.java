package ru.yandex.autotests.mordamobile.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.mordacommonsteps.utils.Selectable;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import java.util.List;

import static org.hamcrest.Matchers.containsString;
import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.CLASS;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 18.04.13
 */
@Name("Блок новостей")
@FindBy(xpath = "//div[contains(@class, 'b-widget  b-news')]")
public class NewsBlock extends HtmlElement {
    @Name("Заголовок")
    @FindBy(xpath = ".//a[contains(@class,'b-widget__title')]")
    public HtmlElement title;

    @Name("Новости")
    @FindBy(xpath =
            ".//li[contains(@class, 'b-menu__item b-widget__list-item') and not(contains(@style, 'display: none;'))]//a")
    public List<HtmlElement> allNews;

    @Name("Категории")
    @FindBy(xpath = ".//ul[@class='b-news-categories']//li[contains(@class, 'b-news-categories-item')]")
    public List<NewsCategory> allCategories;

    public static class NewsCategory extends HtmlElement implements Selectable {

        @FindBy(xpath = ".//span")
        private HtmlElement span;

        @Override
        public void select() {
            if (!isSelected()) {
                span.click();
            }
        }

        @Override
        public void deselect() {
        }

        public boolean isSelected() {
            return hasAttribute(CLASS, containsString("selected-category")).matches(this);
        }
    }
}
