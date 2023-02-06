package ru.yandex.autotests.mainmorda.settingpanels;

import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.mainmorda.blocks.SettingsButton;
import ru.yandex.autotests.mainmorda.blocks.SettingsCheckBox;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

/**
 * User: lipka
 * Date: 30.11.12
 * Time: 16:25
 */

@Name("Блок настройки")
@FindBy(xpath = "//div[@id='widget_pref_form']")
public class WidgetSettings extends HtmlElement {
    @Name("Заголовок 'Настроить'")
    @FindBy(xpath = ".//h3")
    public HtmlElement setupTitle;

    @Name("Кнопка закрытия настроек с крестиком")
    @FindBy(xpath = ".//i[@class='popup__close']")
    public HtmlElement closeSettingsX;

    @Name("Чекбокс 'Автообновление блока'")
    @FindBy(xpath = ".//input[@name='autoreload']/parent::label")
    public SettingsCheckBox autoReloadCheckbox;

    @Name("Кнопка 'OK'")
    @FindBy(xpath = ".//button[@name='save_pref']|//input[@name='save_pref']/..")
    public SettingsButton okButton;

    @Name("Кнопка 'Закрыть'")
    @FindBy(xpath = ".//button[@name='close_pref']|//input[@name='close_pref']/..")
    public SettingsButton closeSettingsButton;

    @Name("Кнопка 'Сбросить настройки'")
    @FindBy(xpath = ".//button[@name='reset_pref']|//input[@name='reset_pref']/..|//span[contains(@class,'b-resetall')]")
    public SettingsButton resetSettingsButton;
}
