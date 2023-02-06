package ru.yandex.autotests.mordamobile.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 18.04.13
 */
@Name("Информер почты")
@FindBy(xpath = "//li[contains(@class, 'b-informer_type_mail')]")
public class MailBlock extends HtmlElement {
    @Name("Иконка")
    @FindBy(xpath = ".//i")
    public HtmlElement icon;

    @Name("Заголовок")
    @FindBy(xpath = ".//div[contains(@class,'b-informer__title')]")
    public HtmlElement title;

    @Name("Ссылка информера")
    @FindBy(xpath = ".//a")
    public HtmlElement mailLink;

    @Name("Текст 'Войти в почту'")
    @FindBy(xpath = ".//div[@class='b-informer__data']")
    public HtmlElement loginText;

    @Name("Текст с количеством писем")
    @FindBy(xpath = ".//div[@class='b-informer__data']")
    public HtmlElement letterText;
}
