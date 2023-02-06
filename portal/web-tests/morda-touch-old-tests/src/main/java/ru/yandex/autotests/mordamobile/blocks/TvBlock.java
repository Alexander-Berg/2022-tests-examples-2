package ru.yandex.autotests.mordamobile.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import java.util.List;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 18.04.13
 */
@Name("Блок новостей")
@FindBy(xpath = "//div[contains(@class, 'b-widget  b-tv')]")
public class TvBlock extends HtmlElement {
    @Name("Иконка")
    @FindBy(xpath = ".//i")
    public HtmlElement icon;

    @Name("Заголовок")
    @FindBy(xpath = ".//a[contains(@class,'b-widget__title')]")
    public HtmlElement title;

    @Name("Список передач")
    @FindBy(xpath = ".//li[contains(@class,'b-widget__list-item')]//a[@class='b-link']")
    public List<TvEvent> allEvents;

    public static class TvEvent extends HtmlElement {
        @Name("Время")
        @FindBy(xpath = ".//span[@class='b-tv__time']")
        public HtmlElement time;

        @Name("Канал")
        @FindBy(xpath = ".//span[@class='b-tv__channel']")
        public HtmlElement program;
    }
}
