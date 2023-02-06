package ru.yandex.autotests.mainmorda.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

/**
 * User: alex89
 * Date: 10.09.12
 */

@FindBy(xpath = ".//")
@Name("Строка с числами котировки")
public class RateCurrency extends HtmlElement {
    @Name("название котировки")
    @FindBy(xpath = ".//div[@class='b-stocks__row-title']/a")
    public HtmlElement rateName;

    @Name("первое число")
    @FindBy(xpath = ".//td[2]")
    public HtmlElement todayValue;

    @Name("разница")
    @FindBy(xpath = ".//td[3]")
    public HtmlElement diff;

    @Name("второе число")
    @FindBy(xpath = ".//td[4]")
    public HtmlElement tomorrowValue;

    public String getRateName() {
        return rateName.getText();
    }

    public String getTodayValue() {
        return todayValue.getText();
    }

    public String getDiff() {
        return diff.getText();
    }

    public String getTomorrowValue() {
        return tomorrowValue.getText();
    }
}
