package ru.yandex.autotests.mainmorda.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import java.util.List;

/**
 * User: eoff
 * Date: 04.02.13
 */
@Name("RSS Виджет")
@FindBy(xpath = "//div[contains(@id,'wd-') and contains(@class,'b-widget-data')]" +
        "[.//div[contains(@class, 'rss')]]")
public class RssWidget extends Widget {

    @Name("Список опций")
    @FindBy(xpath = ".//div[@class='w-rss__list']//div[contains(@class,'w-rss__item')]" +
            "[./div[contains(@class, 'w-rss__item-inner')]]")
    public List<RssOption> rssOptions;

    @Name("Тело виджета")
    @FindBy(xpath = ".//div[contains(@class, 'w-rss__body')]")
    public HtmlElement rssBody;

    @Name("Class виджета")
    @FindBy(xpath = "./div[contains(@id, 'id')]")
    public HtmlElement rssBodyId;

    public static class RssOption extends HtmlElement {
        @Name("Текст")
        @FindBy(xpath = ".//div[@class='w-rss__text']")
        public HtmlElement options;

        @Name("Описание")
        @FindBy(xpath = ".//div[@class='w-rss__description']")
        public HtmlElement description;

        @Name("Картинка")
        @FindBy(xpath = ".//div[contains(@class, 'w-rss__item-inner')]/a")
        public HtmlElement image;
    }

}
