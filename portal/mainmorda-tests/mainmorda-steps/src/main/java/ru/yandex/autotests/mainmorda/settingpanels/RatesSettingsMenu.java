package ru.yandex.autotests.mainmorda.settingpanels;

import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.mainmorda.blocks.SettingsCheckBox;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;
import ru.yandex.qatools.htmlelements.element.Select;

/**
 * Created with IntelliJ IDEA.
 * User: lipka
 * Date: 01.12.12
 * Time: 12:50
 * To change this template use File | Settings | File Templates.
 */
@Name("Настройки котировок")
@FindBy(xpath = "//div[@id='widget_pref_form']")
public class RatesSettingsMenu extends WidgetSettings {
    @Name("Заголовок 'Котировки'")
    @FindBy(xpath = ".//table[@class='multi']/parent::*  ")
    public HtmlElement ratesTitle;

    @Name("Кнопка добавления всех котировок")
    @FindBy(xpath = ".//input[@class='select-add-all-button']")
    public HtmlElement addAllRatesButton;

    @Name("Кнопка добавления одной котировки")
    @FindBy(xpath = ".//input[@class='select-add-button']")
    public HtmlElement addOneRateButton;

    @Name("Кнопка удаления одной котировки")
    @FindBy(xpath = ".//input[@class='select-remove-button']")
    public HtmlElement removeOneRateButton;

    @Name("Кнопка удаления всех котировок")
    @FindBy(xpath = ".//input[@class='select-remove-all-button']")
    public HtmlElement removeAllRatesButton;

    @Name("Чекбокс выделения резких изменения")
    @FindBy(xpath = ".//input[@name='hl']/parent::*")
    public SettingsCheckBox highlightCheckbox;
    //checkbox

//    @Name("Подпись у чекбокса выделения изменений")
//    @FindBy(xpath = ".//label[@for='c3']")
//    public HtmlElement highlightLabel;

//    @Name("Чекбокс 'Автообновление блока'")
//    @FindBy(xpath = ".//input[@name='autoreload']")
//    public SettingsCheckBox autoRenewCheckbox;
//
//    @Name("Подпись у чекбокса автообновления")
//    @FindBy(xpath = ".//label[@for='c4']")
//    public HtmlElement autoRenewLabel;

    @Name("Селектор доступных котировок")
    @FindBy(xpath = ".//select[@class='inSelect']")
    public Select selectRatesToAdd;

    @Name("Селектор отображаемых котировок")
    @FindBy(xpath = ".//select[@class='outSelect']")
    public Select selectRatesToRemove;
}

