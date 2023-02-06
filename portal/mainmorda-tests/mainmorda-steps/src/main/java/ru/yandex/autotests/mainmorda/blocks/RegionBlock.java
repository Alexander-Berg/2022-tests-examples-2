package ru.yandex.autotests.mainmorda.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import java.util.List;

/**
 * User: alex89
 * Date: 13.12.12
 */
@FindBy(xpath = "//div[contains(@class,'b-wdgt-promo b-wrapper-regional')][1]")
@Name("Региональный блок")
public class RegionBlock extends HtmlElement {
    @Name("Ссылки на виджеты")
    @FindBy(xpath = ".//a[contains(@class,'b-wdgt-promo__add')]")
    public List<HtmlElement> widgetLinks;

    @Name("Ссылка на все виджеты для страны")
    @FindBy(xpath = ".//div[@class='b-wdgt-promo__more'][1]//a")
    public HtmlElement allWidgetsCountry;

    @Name("Ссылка на все виджеты для региона")
    @FindBy(xpath = ".//div[@class='b-wdgt-promo__more'][2]//a")
    public HtmlElement allWidgetsRegion;

    @Name("Крестик закрытия")
    @FindBy(xpath = ".//div[@class='b-widget__control']//a")
    public HtmlElement closeCross;

    @Name("Ссылка восстановления")
    @FindBy(xpath = "//div[contains(@class, 'b-wdgt-promo')]//span[@class='b-link__inner']")
    public HtmlElement restore;
}

