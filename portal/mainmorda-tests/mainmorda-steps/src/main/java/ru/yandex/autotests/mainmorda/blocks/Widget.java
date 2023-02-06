package ru.yandex.autotests.mainmorda.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * User: alex89
 * Date: 04.12.12
 */
@Name("Виджет")
public class Widget extends HtmlElement {
    @Name("Крестик 'Закрыть виджет'")
    @FindBy(xpath = ".//ancestor::div[contains(@class,'b-widget')]/div[contains(@class,'control')]" +
            "//a[contains(@class,'close')or contains(@class,'del')]")
    public HtmlElement closeCross;

    @Name("Шестеренка настройки виджета в режиме редактирования")
    @FindBy(xpath = "./ancestor::div[contains(@class,'b-widget')]/div[contains(@class,'control')]" +
            "//a[contains(@class,'setup')]")
    public HtmlElement editIcon;

    @Name("Шестеренка настройки виджета в режиме редактирования")
    @FindBy(xpath = "./ancestor::div[contains(@class,'b-widget')]/div[contains(@class,'control')]" +
            "//a[contains(@class,'send')]")
    public HtmlElement shareIcon;

    @Name("Кнопка возврата в каталог")
    @FindBy(xpath = ".//parent::div/*[@id='retToCat']")
    public HtmlElement catalogButton;

    private static final String WIDGET_ID_PATTERN = "wd-(([_A-Za-z0-9]+)-([0-9]+))";
    Pattern validationPattern = Pattern.compile(WIDGET_ID_PATTERN);

    public String getWidgetId() {
        Matcher idFormat = validationPattern.matcher(getWrappedElement().getAttribute("id"));
        idFormat.matches();
        return idFormat.group(1);
    }

    public String getWidgetName() {
        Matcher idFormat = validationPattern.matcher(getWrappedElement().getAttribute("id"));
        idFormat.matches();
        return idFormat.group(2);
    }

    public String getWidgetNumber() {
        Matcher idFormat = validationPattern.matcher(getWrappedElement().getAttribute("id"));
        idFormat.matches();
        return idFormat.group(3);
    }
}
