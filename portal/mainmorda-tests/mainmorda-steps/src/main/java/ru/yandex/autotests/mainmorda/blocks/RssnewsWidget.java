package ru.yandex.autotests.mainmorda.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import java.util.List;

/**
 * @author Ivan Nikolaev <ivannik@yandex-team.ru>
 */
@Name("Виджет rssnews")
@FindBy(xpath = "//div[contains(@id,'wd-wrapper-_rssnews')]")
public class RssnewsWidget extends HtmlElement {

    @Name("Категории новостей")
    @FindBy(xpath = ".//div[@class='info-block']")
    public List<NewsCategory> newsCategories;

    public static class NewsCategory extends HtmlElement {

        @Name("Ссылка категории новостей")
        @FindBy(xpath = "./a")
        public HtmlElement categoryLink;

        @Name("Список новостей")
        @FindBy(xpath = ".//li")
        public List<NewsItem> newsItems;
    }

    public static class NewsItem extends HtmlElement {

        @Name("Текст новости")
        @FindBy(xpath = ".")
        public HtmlElement title;

        @Name("Ссылка новости")
        @FindBy(xpath = "./a")
        public HtmlElement link;
    }
}
