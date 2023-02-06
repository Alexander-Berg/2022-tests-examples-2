package ru.yandex.autotests.morda.pages.desktop.main.htmlelements;

import org.openqa.selenium.WebElement;
import org.openqa.selenium.support.FindBy;
import org.openqa.selenium.support.ui.Select;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import java.util.List;
import java.util.stream.Collectors;

import static java.lang.Thread.sleep;

public class SettingsSelect extends HtmlElement {

    @FindBy(xpath = ".//button")
    public HtmlElement button;

    @FindBy(xpath = "//div[contains(@class, 'select__popup')]")// and contains(@class, 'popup_visibility_visible')]")
    public SettingsSelectPopup popup;

    @FindBy(xpath = ".//select")
    private HtmlElement select;

    private Select getSelect() {
        return new Select(select);
    }

    public String getSelectedValue() {
        String selectedText = button.getText();
        Select select = getSelect();

        for (WebElement e : select.getOptions()) {
            if (e.getAttribute("textContent").equals(selectedText)) {
                return e.getAttribute("value");
            }
        }

        throw new RuntimeException("Some shit happened");
    }

    public void selectByValue(String value) {
        Select select = getSelect();
        List<String> values = select.getOptions().stream()
                .map(e -> e.getAttribute("value"))
                .collect(Collectors.toList());

        int index = values.indexOf(value);
        if (index >= 0) {
            button.click();
            try {
                sleep(1000);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
            HtmlElement a = popup.items.get(index);
            a.click();
            try {
                sleep(1000);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
    }

    public static class SettingsSelectPopup extends HtmlElement {
        @FindBy(xpath = ".//div[contains(@class, 'select__item')]/span")
        public List<HtmlElement> items;
    }
}
