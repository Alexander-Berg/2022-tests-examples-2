package ru.yandex.autotests.mainmorda.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;


/**
 * User: alex89
 * Date: 04.05.12
 */
@FindBy(xpath = ".//table[2]//tr[1]")
@Name("Строка с нефтяной котировкой")
public class OilString extends HtmlElement {
    @Name("Разница между ценами на нефть")
    @FindBy(xpath = "td[2]")
    public HtmlElement oilDiff;

    @Name("Цена")
    @FindBy(xpath = "td[3]")
    public HtmlElement oilNumeral;

    @Name("Дата")
    @FindBy(xpath = "td[4]")
    public HtmlElement oilData;
}
