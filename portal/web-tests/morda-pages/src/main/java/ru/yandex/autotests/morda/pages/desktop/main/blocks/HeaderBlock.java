package ru.yandex.autotests.morda.pages.desktop.main.blocks;

import org.openqa.selenium.WebDriver;
import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.morda.pages.desktop.main.DesktopMainMorda;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validateable;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validator;
import ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.mordacommonsteps.utils.TextInput;
import ru.yandex.autotests.utils.morda.url.Domain;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import java.util.List;

import static javax.ws.rs.core.UriBuilder.fromUri;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.startsWith;
import static ru.yandex.autotests.morda.pages.desktop.main.blocks.HeaderBlock.HeaderDomik.validateHeaderDomik;
import static ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector.collector;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElement;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElementMatchingTo;
import static ru.yandex.autotests.morda.steps.CheckSteps.url;
import static ru.yandex.autotests.morda.utils.matchers.AllOfDetailedMatcher.allOfDetailed;
import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.HREF;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.PLACEHOLDER;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.TITLE;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Mail.LOGIN;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Mail.LOGIN_LABEL_UP;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Mail.PASSWD_UP;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Mail.PROMO_BUTTON;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;
import static ru.yandex.qatools.htmlelements.matchers.WrapsElementMatchers.hasText;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 01/04/15
 */
@Name("Хедер")
@FindBy(xpath = "//div[contains(@class, 'container') and contains(@class, 'headline')]/div[@class='row']")
public class HeaderBlock extends HtmlElement implements Validateable<DesktopMainMorda> {


    @Name("Ссылка \"Сделать стартовой\"")
    @FindBy(xpath = ".//a[contains(@class, 'sethome__link')]")
    public HtmlElement setHome;

    @Name("Ссылка настройки региона")
    @FindBy(xpath = ".//a[contains(@class, 'geolink')]")
    public HtmlElement setRegion;

    @Name("Ссылка \"Настройка\"")
    @FindBy(xpath = ".//div[contains(@class, 'head-options')]//a[contains(@class, 'dropdown-menu__switcher')]")
    public HtmlElement settings;

    @Name("Ссылка \"Завести почту\"")
    @FindBy(xpath = ".//a[contains(@class, 'domik2__mail-promo')]")
    public HtmlElement createMail;

    @Name("Ссылка \"Почта\"")
    @FindBy(xpath = ".//a[contains(@class, 'domik2__link')]")
    public HtmlElement enter;

    @Name("Меню пользователя")
    @FindBy(xpath = ".//div[contains(@class, 'domik2__dropdown-bg')]//a[contains(@class, 'domik2__usermenu-trigger')]")
    public HtmlElement dropDownUserMenu;

    @Name("Кнопка \"Выйти\"")
    @FindBy(xpath = "//div[contains(@class, 'usermenu_multi_no')]/div[3]/a")
    public HtmlElement logoutButton;

    public HeaderDomik headerDomik;
    public SettingsPopup settingsPopup;

    @Step("{0}")
    public static HierarchicalErrorCollector validateSetHome(HtmlElement setHome,
                                                             Validator<? extends DesktopMainMorda> validator) {
        String setHomeText = getTranslation("home", "head", "edgestripe.startpage", validator.getMorda().getLanguage());
        String setHomeHref = validator.getMorda().getRegion().getDomain().equals(Domain.UA)
                ? "https://download.cdn.yandex.net/element/firefox/homeset/ua/homeset.xpi"
                : "https://download.cdn.yandex.net/element/firefox/homeset/ru/homeset.xpi";

        return collector()
                .check(shouldSeeElement(setHome))
                .check(
                        shouldSeeElementMatchingTo(setHome, allOfDetailed(
                                hasText(setHomeText),
                                hasAttribute(HREF, equalTo(setHomeHref))
                        ))
                );
    }

    @Step("{0}")
    public static HierarchicalErrorCollector validateSetRegion(HtmlElement setRegion,
                                                               Validator<? extends DesktopMainMorda> validator) {
        return collector()
                .check(shouldSeeElement(setRegion))
                .check(
                        shouldSeeElementMatchingTo(setRegion, allOfDetailed(
                                hasText(validator.getCleanvars().getBigCityName()),
                                hasAttribute(HREF, equalTo(url(
                                                validator.getCleanvars().getSetupPages().getRegion().replace("&amp;", "&"),
                                                validator.getMorda().getScheme()))
                                )
                        ))
                );
    }

    @Step("{0}")
    public static HierarchicalErrorCollector validateSettings(HtmlElement settings,
                                                              Validator<? extends DesktopMainMorda> validator) {
        String settingsText = getTranslation("home", "header", "tune", validator.getMorda().getLanguage());
        return collector()
                .check(shouldSeeElement(settings))
                .check(
                        shouldSeeElementMatchingTo(settings, allOfDetailed(
                                hasText(settingsText),
                                hasAttribute(HREF,
                                        equalTo(validator.getCleanvars().getSetupPages().getCommon().replace("&amp;", "&")))

                        ))
                );
    }

    @Step("{0}")
    public static HierarchicalErrorCollector validateCreateMail(HtmlElement createMail,
                                                                Validator<? extends DesktopMainMorda> validator) {
        return collector()
                .check(shouldSeeElement(createMail))
                .check(
                        shouldSeeElementMatchingTo(createMail, allOfDetailed(
                                hasText(getTranslation(PROMO_BUTTON, validator.getMorda().getLanguage())),
                                hasAttribute(HREF,
                                        startsWith(
                                                validator.getMorda().getPassportUrl("passport").toString() +
                                                        "registration/mail")
                                )
                                //startsWith("https://passport.yandex.ru/registration/mail"))
                        ))
                );
    }

    @Step("{0}")
    public static HierarchicalErrorCollector validateEnter(HtmlElement enter,
                                                           Validator<? extends DesktopMainMorda> validator) {
        String loginText = getTranslation("home", "head", "mail", validator.getMorda().getLanguage());
        return collector()
                .check(shouldSeeElement(enter))
                .check(
                        shouldSeeElementMatchingTo(enter, allOfDetailed(
                                hasText(loginText),
                                hasAttribute(HREF, equalTo(validator.getCleanvars().getMail().getHref()))
                        ))
                );
    }

    @Override
    @Step("Check header block")
    public HierarchicalErrorCollector validate(Validator<? extends DesktopMainMorda> validator) {
        return collector()
                .check(shouldSeeElement(this))
                .check(
                        validateSetHome(setHome, validator),
                        validateSetRegion(setRegion, validator),
                        validateSettings(settings, validator),
                        validateCreateMail(createMail, validator),
                        validateEnter(enter, validator),
                        validateHeaderDomik(headerDomik, validator)
                );
    }

    @Name("Домик")
    @FindBy(xpath = ".//form[contains(@class, 'domik2__dropdown-login')]")
    public static class HeaderDomik extends HtmlElement {

        @Name("Поле ввода логина")
        @FindBy(xpath = ".//input[@name='login']")
        public TextInput loginField;

        @Name("Поле ввода пароля")
        @FindBy(xpath = ".//input[@name='passwd']")
        public TextInput passwordField;

        @Name("Вспомнить пароль")
        @FindBy(xpath = ".//a[contains(@class, 'domik2__dropdown-forgot')]")
        public HtmlElement restore;

        @Name("Кнопка \"Войти\"")
        @FindBy(xpath = ".//button[contains(@class, 'auth__button')]")
        public HtmlElement loginButton;

        @Name("Ошибка \"Недопустимый ввод\"")
        @FindBy(xpath = "//div[contains(@class, 'auth__error')]")
        public HtmlElement wrongLogin;

        @Name("Поделяшки")
        @FindBy(xpath = ".//span[contains(@class, 'auth__social-link')]")
        public List<HtmlElement> shareLinks;

        @Name("Поделяшки \"еще\"")
        @FindBy(xpath = ".//span[contains(@class, 'domik2__social-more')]")
        public HtmlElement shareMore;

        @Step("{0}")
        public static HierarchicalErrorCollector validateLoginField(TextInput loginField,
                                                                    Validator<? extends DesktopMainMorda> validator) {
            String loginPlaceholder = getTranslation(LOGIN_LABEL_UP, validator.getMorda().getLanguage());
            return collector()
                    .check(shouldSeeElement(loginField))
                    .check(
                            shouldSeeElementMatchingTo(loginField, hasAttribute(PLACEHOLDER, equalTo(loginPlaceholder)))
                    );
        }

        @Step("{0}")
        public static HierarchicalErrorCollector validatePasswordField(TextInput passwordField,
                                                                       Validator<? extends DesktopMainMorda> validator) {
            String passwordPlaceholder = getTranslation(PASSWD_UP, validator.getMorda().getLanguage());
            return collector()
                    .check(shouldSeeElement(passwordField))
                    .check(
                            shouldSeeElementMatchingTo(passwordField,
                                    hasAttribute(PLACEHOLDER, equalTo(passwordPlaceholder))
                            )
                    );
        }

        @Step("{0}")
        public static HierarchicalErrorCollector validateRestore(HtmlElement restore,
                                                                 Validator<? extends DesktopMainMorda> validator) {
            String restoreTitle = getTranslation("home", "mail", "rememberPwd", validator.getMorda().getLanguage());
            return collector()
                    .check(shouldSeeElement(restore))
                    .check(
                            shouldSeeElementMatchingTo(restore, allOfDetailed(
                                    hasText("?"),
                                    hasAttribute(HREF, equalTo(
                                            fromUri(validator.getMorda().getPassportUrl())
                                                    .path("passport")
                                                    .queryParam("mode", "restore")
                                                    .build()
                                                    .toString())),
                                    hasAttribute(TITLE, equalTo(restoreTitle))
                            ))
                    );
        }

        @Step("{0}")
        public static HierarchicalErrorCollector validateLoginButton(HtmlElement loginButton,
                                                                     Validator<? extends DesktopMainMorda> validator) {
            String loginButtonText = getTranslation(LOGIN, validator.getMorda().getLanguage());
            return collector()
                    .check(shouldSeeElement(loginButton))
                    .check(
                            shouldSeeElementMatchingTo(loginButton, hasText(loginButtonText))
                    );
        }

        @Step("{0}")
        public static HierarchicalErrorCollector validateHeaderDomik(HeaderDomik headerDomik,
                                                                     Validator<? extends DesktopMainMorda> validator) {
            return collector()
                    .check(shouldSeeElement(headerDomik))
                    .check(
                            validateLoginField(headerDomik.loginField, validator),
                            validatePasswordField(headerDomik.passwordField, validator),
                            validateRestore(headerDomik.restore, validator),
                            validateLoginButton(headerDomik.loginButton, validator)
                    );
        }

        @Step("Try login \"{1}:{2}\"")
        public void tryLogin(WebDriver driver, String login, String password) {
            CommonMordaSteps userSteps = new CommonMordaSteps(driver);
            userSteps.shouldSeeElement(this);
            userSteps.shouldSeeElement(this.loginField);
            userSteps.entersTextInInput(this.loginField, login);
            userSteps.shouldSeeElement(this.passwordField);
            userSteps.entersTextInInput(this.passwordField, password);
            userSteps.shouldSeeElement(this.loginButton);
            userSteps.clicksOn(this.loginButton);
        }
    }

    @Name("Меню настроек")
    @FindBy(xpath = "//div[contains(@class, 'popup_head-options_yes')]")
    public static class SettingsPopup extends HtmlElement {

        @Name("Ссылка \"Поставить тему\"")
        @FindBy(xpath = ".//div[@role='menuitem'][1]/a")
        public TextInput setSkin;

        @Name("Ссылка \"Сбросить тему\"")
        @FindBy(xpath = ".//div[@role='menuitem']/a[contains(@href, 'themes/default')]")
        public TextInput resetSkin;

        @Name("Ссылка \"Настроить Яндекс\"")
        @FindBy(xpath = ".//div[@role='menuitem'][2]/a")
        public TextInput tuneYandex;

        @Name("Ссылка \"Изменить город\"")
        @FindBy(xpath = ".//div[@role='menuitem'][3]/a")
        public TextInput setCity;

        @Name("Ссылка \"Другие настройки\"")
        @FindBy(xpath = ".//div[@role='menuitem'][4]/a")
        public TextInput otherSettings;

    }

}
