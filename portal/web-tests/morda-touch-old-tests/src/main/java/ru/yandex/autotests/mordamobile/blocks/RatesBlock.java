package ru.yandex.autotests.mordamobile.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 18.04.13
 */
@Name("Блок котировок")
@FindBy(xpath = "//div[contains(@class, 'b-widget  b-stocks')]")
public class RatesBlock extends HtmlElement {
    @Name("Заголовок котировок")
    @FindBy(xpath = ".//span[contains(@class,'b-widget__title')]")
    public HtmlElement title;

    @Name("Курс доллара")
    @FindBy(xpath = ".//tr[@class='b-table__row'][2]")
    public RateElement usd;

    @Name("Курс евро")
    @FindBy(xpath = ".//tr[@class='b-table__row'][3]")
    public RateElement eur;

    @Name("Курс нефти")
    @FindBy(xpath = ".//tr[@class='b-table__row'][4]")
    public RateElement oil;

    @Name("Текст сегодня")
    @FindBy(xpath = ".//table[1]//tr[1]//th[2]")
    public HtmlElement today;

    @Name("Текст разница")
    @FindBy(xpath = ".//table[1]//tr[1]//th[3]")
    public HtmlElement diff;

    @Name("Текст завтра")
    @FindBy(xpath = ".//div[contains(@class, 'b-widget b-rates')]//table[1]//tr[1]//th[4]")
    public HtmlElement tomorrow;

    public static class RateElement extends HtmlElement {
        @Name("Название котировки")
        @FindBy(xpath = ".//a")
        public HtmlElement titleLink;

        @Name("Текущее значение")
        @FindBy(xpath = "./td[2]")
        public HtmlElement todayValue;

        @Name("Разница")
        @FindBy(xpath = "./td[3]")
        public HtmlElement diff;

        @Name("Завтрашнее значени")
        @FindBy(xpath = "./td[4]")
        public HtmlElement tomorrowValue;
    }
}
