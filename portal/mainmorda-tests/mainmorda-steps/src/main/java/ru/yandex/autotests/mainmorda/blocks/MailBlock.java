package ru.yandex.autotests.mainmorda.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.mordacommonsteps.utils.CheckBox;
import ru.yandex.autotests.mordacommonsteps.utils.TextInput;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

/**
 * User: alex89
 * Date: 06.10.12
 */
@FindBy(xpath = "//form[contains(@class, 'auth_js_inited')]")
@Name("Домик")
public class MailBlock extends HtmlElement {

    @Name("Ссылка Почта")
    @FindBy(xpath = "//div[contains(@class, 'domik__title')]//a")
    public HtmlElement title;

    @Name("Кнопка Завести почту")
    @FindBy(xpath = "//div[contains(@class, 'auth__register')]//a")
    public HtmlElement createAccountButton;

    @Name("Подсказка в поле Логин")
    @FindBy(xpath = ".//div[contains(@class, 'auth__username')]//label")
    public HtmlElement loginText;

    @Name("Поле ввода Логин")
    @FindBy(xpath = ".//div[contains(@class, 'auth__username')]//input")
    public TextInput loginInput;

    @Name("Подсказка в поле Пароль")
    @FindBy(xpath = ".//div[contains(@class, 'auth__password')]//label")
    public HtmlElement passwordText;

    @Name("Поле ввода Пароль")
    @FindBy(xpath = ".//div[contains(@class, 'auth__password')]//input")
    public TextInput passwordInput;

    @Name("Чекбокс Чужой компьютер")
    @FindBy(xpath = "//div[contains(@class, 'auth__haunter')]//input")
    public CheckBox alienPCCheckbox;

    @Name("Текст чекбокса Чужой компьютер")
    @FindBy(xpath = "//div[contains(@class, 'auth__haunter')]//label")
    public HtmlElement alienPCCheckboxText;

    @Name("Текст кнопки Войти")
    @FindBy(xpath = ".//div[contains(@class, 'auth__button')]//button/span")
    public HtmlElement loginButtonText;

    @Name("Кнопка Войти")
    @FindBy(xpath = ".//div[contains(@class, 'auth__button')]//button")
    public HtmlElement loginButton;

    @Name("Ссылка Вспомнить пароль")
    @FindBy(xpath = ".//div[contains(@class, 'auth__remember')]/a")
    public HtmlElement remindPwd;

    @Name("Сообщение об ошибке")
    @FindBy(xpath = "//div[contains(@class, 'popup_to_left')]//div[contains(@class, 'auth__error')]")
    public HtmlElement errorMessage;

    @Name("Кнопка-стрелка 'Свернуть'")
    @FindBy(xpath = "//div[contains(@class, 'b-topbar__toggler')]/span")
    public HtmlElement foldButton;

    @Name("Иконка-стрелка 'Свернуть'")
    @FindBy(xpath = "//div[contains(@class, 'b-topbar__toggler')]/span/img")
    public HtmlElement foldIcon;
}
