package ru.yandex.autotests.mainmorda.blocks;

import org.openqa.selenium.WebElement;
import org.openqa.selenium.support.FindBy;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import java.util.List;

/**
 * User: alex89
 * Date: 04.05.12
 */

@FindBy(xpath = "//div[contains(@class,'b-wrapper-stocks')]")
@Name("Блок котировок")
public class RatesBlock extends Widget {
    @Name("Котировка №")
    @FindBy(xpath = ".//table//tr[not(@class)]//div[@class='b-stocks__row-title']/a")
    public List<HtmlElement> ratesLinks;

    @Name("Заголовок блока котировок")
    @FindBy(xpath = ".//div[contains(@class,'title')]")
    public HtmlElement ratesTitle;

    @Name("Текст сегодня/покупка")
    @FindBy(xpath = ".//table[contains(@class,'b-stocks-i')]/tbody/tr[@class='head']/th[1]")
    public HtmlElement today;

    @Name("Все котировки")
    @FindBy(xpath = ".//span[contains(@class, 'b-stocks_') and contains(@class, 'adaptive2')]/../../td[1]")
    public List<WebElement> allRates;

    @Name("Горячие котировки")
    @FindBy(xpath = ".//span[contains(@class, '-value-hot') and contains(@class, 'adaptive2')]/../../td[1]")
    public List<WebElement> hotRates;

    @Name("Текст завтра/продажа")
    @FindBy(xpath = ".//table[contains(@class,'b-stocks-i') and contains(@class, 'currency')]" +
            "/tbody/tr[@class='head']/th[2]")
    public HtmlElement tomorrow;

    @Name("Строка с числами котировки №")
    @FindBy(xpath = ".//table[contains(@class,'currency') or contains(@class,'cash')]//tr[not(@class)]")
    public List<RateStructure> ratesStrings;

    @Name("Строка с числами котировки [currency] №")
    @FindBy(xpath = ".//table[contains(@class,'currency')]//tr[not(@class)]")
    public List<RateCurrency> ratesStringsCurrency;

    @Name("Строка с числами котировки [cash] №")
    @FindBy(xpath = ".//table[contains(@class,'cash')]//tr[not(@class)]")
    public List<RateCash> ratesStringsCash;

    @Name("Кнопка 'Переместить наверх'")
    @FindBy(xpath = ".//a[contains(@class,'toggle-up')]")
    public HtmlElement toggleUpButton;

    public OilString oilString;
}