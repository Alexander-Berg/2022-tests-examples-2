package ru.yandex.autotests.mordamobile.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import java.util.List;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 18.04.13
 */
@Name("Блок афиши")
@FindBy(xpath = "//div[contains(@class, 'b-widget  b-afisha')]")
public class AfishaBlock extends HtmlElement {
    @Name("Иконка")
    @FindBy(xpath = ".//i")
    public HtmlElement icon;

    @Name("Заголовок")
    @FindBy(xpath = ".//a[contains(@class,'b-widget__title')]")
    public HtmlElement title;

    @Name("Список передач")
    @FindBy(xpath = ".//a[@class='b-link'][not(.//div[@class='b-afisha__when'] or .//div[contains(@class, 'b-afisha-promo__content')])]")
    public List<AfishaEvent> allEvents;

    @Name("Премьеры")
    @FindBy(xpath = ".//a[@class='b-link'][.//div[@class='b-afisha__when']]")
    public List<AfishaEvent> premiers;

    public static class AfishaEvent extends HtmlElement {
        @Name("Жанр")
        @FindBy(xpath = ".//div[@class='b-afisha__genre']")
        public HtmlElement genre;

        @Name("Время премьеры")
        @FindBy(xpath = ".//div[@class='b-afisha__when']")
        public HtmlElement when;
    }
}
