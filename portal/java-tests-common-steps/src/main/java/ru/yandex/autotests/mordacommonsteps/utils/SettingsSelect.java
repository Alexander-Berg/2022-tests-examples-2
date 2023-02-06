package ru.yandex.autotests.mordacommonsteps.utils;

import org.openqa.selenium.support.FindBy;
import ru.yandex.qatools.htmlelements.element.HtmlElement;
import ru.yandex.qatools.htmlelements.element.Select;

import java.util.List;

public class SettingsSelect extends HtmlElement {

    @FindBy(xpath = ".//button")
    public HtmlElement button;

    @FindBy(xpath = "//div[contains(@class, 'select__popup')]")
    public SettingsSelectPopup popup;

    @FindBy(xpath = ".//select")
    private HtmlElement select;

    public Select getSelect() {
        return new Select(select);
    }

    public String getSelectedOption(){
        return getSelect().getAllSelectedOptions().stream()
                .findFirst()
                .orElseThrow(RuntimeException::new)
                .getAttribute("value");
    }

    public static class SettingsSelectPopup extends HtmlElement {
        @FindBy(xpath = ".//div[contains(@class, 'select__item')]/span")
        public List<HtmlElement> items;
    }
}
