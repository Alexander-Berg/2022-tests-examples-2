package ru.yandex.autotests.mainmorda.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import java.util.List;

/**
 * User: eoff
 * Date: 27.02.13
 */
@FindBy(xpath = "//div[contains(@class, 'b-wrapper-geo')]")
@Name("Геоблок")
public class GeoBlock extends Widget {

    @Name("Ссылка Карта такого-то города")
    @FindBy(xpath = ".//div[contains(@class,'title')]//a")
    public HtmlElement mapTitle;

    @Name("Шестерёнка настройки региона")
    @FindBy(xpath = ".//div[contains(@class,'title')]//a[contains(@class,'setup_icon')]")
    public HtmlElement regionSetupIcon;

    @Name("Все иконки")
    @FindBy(xpath = ".//a[contains(@class, 'b-region__icons__item')]")
    public List<GeoIcon> allIcons;

    @Name("Все постояныне ссылки")
    @FindBy(xpath = "//div[contains(@class, 'b-region__links__item')]" +
            "/a[not(@href='') and not(./i[contains(@class, b-ico-tick)])]")
    public List<HtmlElement> allPermanentLinks;

    @Name("Появляющаяся ссылка при изменении размера окна")
    @FindBy(xpath = "//div[contains(@class, 'b-region__links__item_0')]")
    public HtmlElement adaptiveLink;

    @Name("Пропадающая иконка при изменении размера окна")
    @FindBy(xpath = ".//a[contains(@class, 'b-region__icons__item_4')]/span")
    public HtmlElement adaptiveIcon;

    public static class GeoIcon extends HtmlElement {
        @Name("Иконка poi")
        @FindBy(xpath = ".//span[contains(@class, 'b-region__icons__icon')]/i[1]")
        public HtmlElement icon;

        @Name("Подпись")
        @FindBy(xpath = ".//span[contains(@class, 'b-region__icons__text')]")
        public HtmlElement balloon;
    }

}
