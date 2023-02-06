package ru.yandex.autotests.mainmorda.blocks;

import org.openqa.selenium.WebElement;
import ru.yandex.qatools.htmlelements.element.HtmlElement;
import ru.yandex.qatools.htmlelements.element.Select;

import java.util.ArrayList;
import java.util.List;

/**
 * User: eoff
 * Date: 17.12.12
 */
public class SettingsSelect extends Select {
    public SettingsSelect(WebElement wrappedElement) {
        super(wrappedElement);
    }

    public List<HtmlElement> getOptionsAsHtmlElements() {
        List<WebElement> elements = getOptions();
        List<HtmlElement> result = new ArrayList<HtmlElement>();
        for (WebElement element : elements) {
            HtmlElement newElement = new HtmlElement();
            newElement.setWrappedElement(element);
            newElement.setName(element.getText());
            result.add(newElement);
        }
        return result;
    }

    public HtmlElement getFirstSelectedOptionAsHtmlElement() {
        WebElement option = getFirstSelectedOption();
        HtmlElement result = new HtmlElement();
        result.setName(option.getTagName());
        result.setWrappedElement(option);
        return result;
    }
}