package ru.yandex.autotests.mainmorda.settingpanels;

import org.openqa.selenium.support.FindBy;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

/**
 * User: eoff
 * Date: 25.12.12
 */
@Name("Настройки трафика")
@FindBy(xpath = "//*[@id='wd-_traffic-1' or (@id='widget_pref_form_data')]")
public class TrafficSettingsMenu extends HtmlElement {
    @Name("Текст 'Загруженность дорог на вашем маршруте'")
    @FindBy(xpath = "//div[@class='b-jam-title']")
    public HtmlElement titleText;

    @Name("Кнопка 'проложить'")
    @FindBy(xpath = "//input[@class='b-refresh']")
    public HtmlElement refreshButton;

    @Name("Текст 'Дом'")
    @FindBy(xpath = "//table[contains(@class, 'addr')]//tr[1]//span[@class='b-user-label__static__text']")
    public HtmlElement homeText;

    @Name("Текст 'Работа'")
    @FindBy(xpath = "//table[contains(@class, 'addr')]//tr[2]//span[@class='b-user-label__static__text']")
    public HtmlElement workText;

    @Name("Текст 'инфо'")
    @FindBy(xpath = "//div[@class='b-info']/span")
    public HtmlElement infoText;

    @Name("Блок кнопок")
    @FindBy(xpath = "//div[contains(@class, 'ctrls')]")
    public ButtonsBlock buttonsBlock;

    public static class ButtonsBlock extends HtmlElement {
        @Name("Кнопка 'сохранить'")
        @FindBy(xpath = ".//button[contains(@class, 'b-saveall')]")
        public HtmlElement saveButton;

        @Name("Кнопка 'отмена'")
        @FindBy(xpath = ".//button[contains(@class, 'cancelall')]")
        public HtmlElement cancelButton;

        @Name("Кнопка 'сбросить настройки'")
        @FindBy(xpath = ".//span[contains(@class, 'resetall')]")
        public HtmlElement resetButton;
    }
}
