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
public class RateCash extends HtmlElement {
    @Name("название котировки")
    @FindBy(xpath = ".//div[@class='b-stocks__row-title']/a")
    public HtmlElement rateName;

    @Name("первое число наличных курсов")
    @FindBy(xpath = ".//td[2]")
    public HtmlElement buyValue;

    @Name("второе число наличных курсов")
    @FindBy(xpath = ".//td[3]")
    public HtmlElement sellValue;

    public String getRateName() {
        return rateName.getText();
    }

    public String getBuyValue() {
        return buyValue.getText();
    }

    public String getSellValue() {
        return sellValue.getText();
    }
}
