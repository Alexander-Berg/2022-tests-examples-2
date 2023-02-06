package ru.yandex.autotests.mordamobile.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.mordacommonsteps.utils.TextInput;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

/**
 * User: ivannik
 * Date: 05.03.14
 * Time: 12:46
 */
@Name("Домик авторизации")
@FindBy(xpath = "//div[contains(@class,'b-domik-popup_shown_yes')]")
public class LoginPopupBlock extends HtmlElement {

    @Name("Крестик 'Закрыть'")
    @FindBy(xpath = ".//div[@class='b-domik__close']")
    public HtmlElement closeCross;

    @Name("Заголовок домика")
    @FindBy(xpath = ".//h3[@class='b-domik__title']")
    public HtmlElement title;

    @Name("Кнопка 'Вспомнить пароль'")
    @FindBy(xpath = ".//a[contains(@class, 'b-domik__rem')]")
    public HtmlElement remindPasswordButton;

    @Name("Кнопка 'Регистрация'")
    @FindBy(xpath = ".//a[contains(@class, 'b-domik__reg')]")
    public HtmlElement registrationButton;

    @Name("Поле ввода 'Логин'")
    @FindBy(xpath = ".//input[@id='auth_login']")
    public TextInput loginInput;

    @Name("Крестик очистки поля 'Логин'")
    @FindBy(xpath = ".//input[@id='auth_login']/../i")
    public HtmlElement clearLoginCross;

    @Name("Поле ввода 'Пароль'")
    @FindBy(xpath = ".//input[@id='auth_password']")
    public TextInput passwordInput;

    @Name("Крестик очистки поля 'Пароль'")
    @FindBy(xpath = ".//input[@id='auth_password']/../i")
    public HtmlElement clearPasswordCross;

    @Name("Кнопка 'Войти'")
    @FindBy(xpath = ".//button[contains(@class,'b-domik__auth-button')]")
    public HtmlElement authButton;

    @Name("Кнопка входа через vk")
    @FindBy(xpath = ".//div[@class='b-auth-social__link b-auth-social__vk']")
    public HtmlElement vkLoginButton;

    @Name("Кнопка входа через fb")
    @FindBy(xpath = ".//div[@class='b-auth-social__link b-auth-social__fb']")
    public HtmlElement fbLoginButton;

    @Name("Кнопка входа через tw")
    @FindBy(xpath = ".//div[@class='b-auth-social__link b-auth-social__tw']")
    public HtmlElement twLoginButton;

    @Name("Кнопка входа через mr")
    @FindBy(xpath = ".//div[@class='b-auth-social__link b-auth-social__mr']")
    public HtmlElement mrLoginButton;

    @Name("Кнопка входа через gg")
    @FindBy(xpath = ".//div[@class='b-auth-social__link b-auth-social__gg']")
    public HtmlElement ggLoginButton;

    @Name("Кнопка входа через ok")
    @FindBy(xpath = ".//div[@class='b-auth-social__link b-auth-social__ok']")
    public HtmlElement okLoginButton;

    @Name("Закрытый домик авторизации")
    public HtmlElement closedDomik;
}
