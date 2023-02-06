package ru.yandex.autotests.mordamobile.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import java.util.List;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 18.04.13
 */
@Name("Блок промо")
@FindBy(xpath = "//div[contains(@class, 'b-widget b-poi-promo')]")
public class PoiBlock extends HtmlElement {
    @Name("Иконка")
    @FindBy(xpath = ".//i")
    public HtmlElement icon;

    @Name("Заголовок")
    @FindBy(xpath = ".//a[contains(@class,'b-widget__title')]")
    public HtmlElement title;

    @Name("Элементы в расписании")
    @FindBy(xpath = ".//li[contains(@class, 'b-menu__item')]//*[contains(@class, 'b-link')]")
    public List<PoiItem> allItems;

    public static class PoiItem extends HtmlElement {
        @Name("Иконка")
        @FindBy(xpath = ".//div[contains(@class,'b-poi-icon')]")
        public HtmlElement icon;
    }
}
