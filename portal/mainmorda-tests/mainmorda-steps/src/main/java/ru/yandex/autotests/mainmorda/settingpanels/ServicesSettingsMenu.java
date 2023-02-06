package ru.yandex.autotests.mainmorda.settingpanels;

import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.mainmorda.blocks.SettingsCheckBox;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;
import ru.yandex.qatools.htmlelements.element.Select;

/**
 * User: eoff
 * Date: 28.01.13
 */
@Name("Настройки блока сервисов")
@FindBy(xpath = "//div[@id='widget_pref_form']")
public class ServicesSettingsMenu extends WidgetSettings {
    @Name("Заголовок 'Сервисы'")
    @FindBy(xpath = ".//table[@class='multi']/parent::*  ")
    public HtmlElement servicesTitle;

    @Name("Копка добавления всех сервисов")
    @FindBy(xpath = ".//input[contains(@class,'add-all-button')]")
    public HtmlElement addAllServicesButton;

    @Name("Кнопка добавления одного сервиса")
    @FindBy(xpath = ".//input[contains(@class,'add-button')]")
    public HtmlElement addOneServiceButton;

    @Name("Кнопка удаления одного сервиса")
    @FindBy(xpath = ".//input[contains(@class,'remove-button')]")
    public HtmlElement removeOneServiceButton;

    @Name("Кнопка удаления всех сервисов")
    @FindBy(xpath = ".//input[contains(@class,'remove-all-button')]")
    public HtmlElement removeAllServicesButton;

    @Name("Список доступных сервисов")
    @FindBy(xpath = ".//select[@class='inSelect']")
    public Select selectServicesToAdd;

    @Name("Селектор отображаемых сервисов")
    @FindBy(xpath = ".//select[@class='outSelect']")
    public Select selectServicesToRemove;

    @Name("Чекбокс подписей под сервисами")
    @FindBy(xpath = ".//input[@name='nosigns']/parent::label")
    public SettingsCheckBox noSignsCheckBox;
}

