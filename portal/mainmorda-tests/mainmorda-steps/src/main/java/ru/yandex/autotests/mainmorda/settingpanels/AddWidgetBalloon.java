package ru.yandex.autotests.mainmorda.settingpanels;

import org.openqa.selenium.support.FindBy;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

/**
 * User: alex89
 * Date: 11.12.12
 */
@Name("Всплывающее окно добавления виджета")
@FindBy(xpath = "//div[contains(concat(' ',@class,' '), ' b-wdgt-hint ')]")
public class AddWidgetBalloon extends HtmlElement {
    @Name("Сообщение 'Вы действительно хотите добавить этот виджет?'")
    @FindBy(xpath = ".//*[contains(@class,'message')]")
    public HtmlElement addMessage;

    @Name("Кнопка добавить виджет")
    @FindBy(xpath = ".//button[contains(@class,'b-wdgt-hint__accept')]")
    public HtmlElement addButton;

    @Name("Кнопка удалить виджет")
    @FindBy(xpath = ".//button[contains(@class,'b-wdgt-hint__reject')]")
    public HtmlElement deleteButton;

    @Name("Подпись 'Яндекс не имеет прямого отношения к содержимому виджета.'")
    @FindBy(xpath = ".//*[contains(@class,'no-yandex')]")
    public HtmlElement noYandexMessage;
}
