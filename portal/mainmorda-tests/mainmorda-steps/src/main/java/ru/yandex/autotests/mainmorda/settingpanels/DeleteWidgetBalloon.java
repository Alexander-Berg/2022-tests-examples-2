package ru.yandex.autotests.mainmorda.settingpanels;

import org.openqa.selenium.support.FindBy;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

/**
 * User: alex89
 * Date: 25.12.12
 */

@Name("Всплывающее окно удаления виджета")
@FindBy(xpath = "//*[@id='b-blame']")
public class DeleteWidgetBalloon extends HtmlElement {
    @Name("Сообщение 'Вы действительно хотите удалить этот виджет?'")
    @FindBy(xpath = ".//div[contains(@class,'content')]/div[contains(@class,'b-wdgt-remove__message')]")
    public HtmlElement deleteMessage;

    @Name("Кнопка удалить виджет")
    @FindBy(xpath = ".//*[@id='del-wdgt']")
    public HtmlElement deleteButton;

    @Name("Кнопка оставить виджет")
    @FindBy(xpath = ".//*[@id='keep-wdgt']")
    public HtmlElement keepButton;

    @Name("Ccылка 'Пожаловаться'")
    @FindBy(xpath = ".//a[@id='blame-wdgt']")
    public HtmlElement complainsLink;
}
