package ru.yandex.autotests.mainmorda.settingpanels;

import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.mainmorda.blocks.SettingsSelect;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

/**
 * User: eoff
 * Date: 14.01.13
 */
@Name("Настройки электричек")
@FindBy(xpath = "//*[contains(@id,'etrains')]")
public class EtrainsSettingsMenu extends HtmlElement {
    @Name("Селектор 'Город'")
    @FindBy(xpath = ".//select[@name='rasp_city']")
    public SettingsSelect city;

    @Name("Селектор 'Направление'")
    @FindBy(xpath = ".//select[@name='rasp_direction']")
    public SettingsSelect direction;

    @Name("Селектор 'Откуда'")
    @FindBy(xpath = ".//select[@name='rasp_from']")
    public SettingsSelect from;

    @Name("Селектор 'Куда'")
    @FindBy(xpath = ".//select[@name='rasp_to']")
    public SettingsSelect to;

    @Name("Селектор количества электричек")
    @FindBy(xpath = ".//select[@name='n']")
    public SettingsSelect number;

    @Name("Текст про количество электричек")
    @FindBy(xpath = ".//span[@name='n-label']")
    public HtmlElement numberText;

    @Name("Сообщение, что прямого сообщения нет")
    @FindBy(xpath = ".//div[@id='no_routes']")
    public HtmlElement noRoutes;

    @Name("Кнопка 'OK'")
    @FindBy(xpath = ".//input[contains(@id,'save')]")
    public HtmlElement okButton;

    @Name("Кнопка 'Закрыть'")
    @FindBy(xpath = ".//div[@class='b-widget-settings__buttons']/input[2]")
    public HtmlElement closeSettingsButton;

    @Name("Кнопка 'Сбросить настройки'")
    @FindBy(xpath = ".//input[contains(@id,'clear')]")
    public HtmlElement resetSettingsButton;

    @Name("Заголовок 'Настроить'")
    @FindBy(xpath = "//div[@id='widget_pref_form']//h3[@class='b-modal-window__head']")
    public HtmlElement setupTitle;

    @Name("Кнопка закрытия настроек с крестиком")
    @FindBy(xpath = "//*[@id='widget_pref_form']//i[contains(@class, 'popup__close')]")
    public HtmlElement closeSettingsX;
}
