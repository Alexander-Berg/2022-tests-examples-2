package ru.yandex.autotests.mordamobile.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

/**
 * User: ivannik
 * Date: 10.01.14
 * Time: 13:41
 */
@Name("Блок денег")
@FindBy(xpath = "//*[contains(@class, 'b-informer_type_money') or contains(@class, 'b-widget b-money')]")
public class MoneyBlock extends HtmlElement {

    @Name("Заголовок")
    @FindBy(xpath = ".//div[contains(@class, 'title')]")
    public HtmlElement title;

    @Name("Иконка")
    @FindBy(xpath = ".//i")
    public HtmlElement icon;

    @Name("Количество денег")
    @FindBy(xpath = ".//div[contains(@class, 'data')]")
    public HtmlElement numMoney;

    @Name("Ссылка")
    @FindBy(xpath = ".//a")
    public HtmlElement moeneyLink;
}
