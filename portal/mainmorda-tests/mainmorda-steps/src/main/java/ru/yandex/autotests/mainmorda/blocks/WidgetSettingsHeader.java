package ru.yandex.autotests.mainmorda.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

/**
 * User: eoff
 * Date: 29.11.12
 */
@FindBy(xpath = "//div[contains(@class,'wdgt-settings')]")
public class WidgetSettingsHeader extends HtmlElement {
    @Name("Ссылка 'в каталоге n виджетов'")
    @FindBy(xpath = ".//span[@id='wdgt-add']")
    public HtmlElement inCatalogWidgets;

    @Name("Ссылка 'n виджетов для региона'")
    @FindBy(xpath = ".//span[@id='wdgt-add-region']")
    public HtmlElement inRegionWidgets;

    @Name("Кнопка сохранения")
    @FindBy(xpath = ".//*[@id='save-view']")
    public HtmlElement saveButton;

    @Name("Кнопка отмены")
    @FindBy(xpath = ".//*[@id='close-settings']")
    public HtmlElement cancelButton;

    @Name("Кнопка обратить изменения")
    @FindBy(xpath = ".//*[@id='undoLink']")
    public HtmlElement undoButton;

    @Name("Кнопка сброса настроек")
    @FindBy(xpath = ".//*[@id='reset-view']")
    public HtmlElement resetButton;

    @Name("Сообщение об ошибке")
    @FindBy(xpath = ".//span[@id='errorMessage']")
    public HtmlElement errorMessageText;

}
