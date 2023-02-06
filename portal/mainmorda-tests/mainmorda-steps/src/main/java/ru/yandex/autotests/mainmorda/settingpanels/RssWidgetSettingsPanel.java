package ru.yandex.autotests.mainmorda.settingpanels;

import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.mainmorda.blocks.SettingsCheckBox;
import ru.yandex.autotests.mainmorda.blocks.SettingsSelect;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

/**
 * User: eoff
 * Date: 03.02.13
 */
@Name("Блок настройки виджетов из раздела новостей")
@FindBy(xpath = "//div[@id='widget_pref_form']")
public class RssWidgetSettingsPanel extends WidgetSettings {

    @Name("Подпись 'Внешний вид'")
    @FindBy(xpath = ".//label[@for='c2']")
    public HtmlElement typeText;

    @Name("Селектор 'Внешний вид'")
    @FindBy(xpath = ".//select[@name='type']")
    public SettingsSelect type;

    @Name("Подпись 'Высота виджета'")
    @FindBy(xpath = ".//label[@for='c3']")
    public HtmlElement heightText;

    @Name("Селектор 'Высота виджета'")
    @FindBy(xpath = ".//select[@name='wht']")
    public SettingsSelect height;

    @Name("Чекбокс 'Показывать только заголовки'")
    @FindBy(xpath = ".//label[@for='c4']")
    public SettingsCheckBox noText;


}
