package ru.yandex.autotests.mainmorda.settingpanels;

import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.mainmorda.blocks.SettingsCheckBox;
import ru.yandex.autotests.mainmorda.blocks.SettingsSelect;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;
import ru.yandex.qatools.htmlelements.element.Select;

/**
 * User: lipka
 * Date: 03.12.12
 * Time: 15:16
 */
@Name("Настройки телепрограммы")
@FindBy(xpath = "//div[@id='widget_pref_form']")
public class TVSettingMenu extends WidgetSettings {
    @Name("Заголовок 'ТВ-каналы'")
    @FindBy(xpath = ".//table[@class='multi']/parent::*  ")
    public HtmlElement tvChannelsTitle;

    @Name("Копка добавления всех телеканалов")
    @FindBy(xpath = ".//input[contains(@class,'add-all-button')]")
    public HtmlElement addAllChannelsButton;

    @Name("Кнопка добавления одного телеканала")
    @FindBy(xpath = ".//input[contains(@class,'add-button')]")
    public HtmlElement addOneChannelButton;

    @Name("Кнопка удаления одного телеканала")
    @FindBy(xpath = ".//input[contains(@class,'remove-button')]")
    public HtmlElement removeOneChannelButton;

    @Name("Кнопка удаления всех телеканалов")
    @FindBy(xpath = ".//input[contains(@class,'remove-all-button')]")
    public HtmlElement removeAllChannelsButton;

    @Name("Список доступных телеканалов")
    @FindBy(xpath = ".//select[@class='inSelect']")
    public Select selectChannelsToAdd;

    @Name("Селектор отображаемых телеканалов")
    @FindBy(xpath = ".//select[@class='outSelect']")
    public Select selectChannelsToRemove;

    @Name("Чекбокс ночного режима")
    @FindBy(xpath = ".//input[@name='noannounces']/parent::label")
    public SettingsCheckBox nightTVCheckbox;

    @Name("Селектор числа передач")
    @FindBy(xpath = ".//select[@name='quantity']")
    public SettingsSelect selectProgrammeLength;

    @Name("Подпись селектора числа передач")
    @FindBy(xpath = ".//label[@for='c2']")
    public HtmlElement programmeLengthLabel;
}
