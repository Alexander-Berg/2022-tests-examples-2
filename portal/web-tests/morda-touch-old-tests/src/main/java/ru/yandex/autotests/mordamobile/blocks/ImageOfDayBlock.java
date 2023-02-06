package ru.yandex.autotests.mordamobile.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 18.04.13
 */
@Name("Блок новостей")
@FindBy(xpath = "//div[contains(@class, 'b-widget b-photo')]")
public class ImageOfDayBlock extends HtmlElement {
    @Name("Иконка")
    @FindBy(xpath = ".//i")
    public HtmlElement icon;

    @Name("Заголовок")
    @FindBy(xpath = ".//a[contains(@class,'b-widget__title')]")
    public HtmlElement title;

    @Name("Картинка")
    @FindBy(xpath = ".//a[@class='b-link b-widget__content']")
    public HtmlElement photoLink;

    @Name("Картинка")
    @FindBy(xpath = ".//a[@class='b-link b-widget__content']//img")
    public HtmlElement photo;
}
