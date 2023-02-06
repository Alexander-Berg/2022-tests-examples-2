package ru.yandex.autotests.mainmorda.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

/**
 * User: alex89
 * Date: 17.07.12
 * Элементы teaser-а на новой "морде".
 */
@Name("Тизер")
@FindBy(xpath = "//div[contains(@class,'teaser')]")
public class TeaserBlock extends Widget {
    @Name("Ссылка картинки в тизере")
    @FindBy(xpath = ".//a[contains(@class,'g-png')]")
    public HtmlElement promoImageLink;

    @Name("Картинка в тизере")
    @FindBy(xpath = ".//a[contains(@class,'g-png')]/img")
    public HtmlElement promoImage;

    @Name("Промо-ссылка")
    @FindBy(xpath = ".//h2[@class='b-promo__title']/a")
    public HtmlElement promoLink;

    @Name("Текст с описанием под Промо-ссылкой")
    @FindBy(xpath = ".//div[@class='b-promo__description']")
    public HtmlElement promoDescription;

    @Name("Крестик 'Закрыть виджет'")
    @FindBy(xpath = ".//parent::div/div[@class='b-widget__control']/a")
    public HtmlElement closeCross;
}