package ru.yandex.autotests.mainmorda.settingpanels;

import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.mainmorda.blocks.SettingsSelect;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

/**
 * User: lipka
 * Date: 30.11.12
 * Time: 21:10
 */
@Name("Настройки новостей")
@FindBy(xpath = "//div[@id='widget_pref_form']")
public class NewsSettingsMenu extends WidgetSettings {
    @Name("Выпадушка нумерации")
    @FindBy(xpath = ".//select[@id='c2']")
    public SettingsSelect enumerationSelect;

    @Name("Подпись у выпадушки нумерации")
    @FindBy(xpath = ".//label[@for='c2']")
    public HtmlElement enumerationSelectLabel;

    @Name("Селектор выбора языка новостей")
    @FindBy(xpath = ".//select[@name='lang']")
    public SettingsSelect languageSelect;

    @Name("Подпись селектора выбора языка")
    @FindBy(xpath = ".//label[@for='c1']")
    public HtmlElement languageSelectLabel;
}