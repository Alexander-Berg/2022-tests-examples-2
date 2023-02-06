package ru.yandex.autotests.morda.pages.desktop.yaru.htmlelements;

import org.openqa.selenium.Cookie;
import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.morda.pages.desktop.yaru.DesktopYaruMorda;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validateable;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validator;
import ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector;
import ru.yandex.autotests.morda.utils.cookie.WebDriverCookieUtils;
import ru.yandex.autotests.utils.morda.language.Dictionary;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import static javax.ws.rs.core.UriBuilder.fromUri;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.startsWith;
import static ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector.collector;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElement;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElementMatchingTo;
import static ru.yandex.autotests.morda.utils.cookie.CookieUtilsFactory.cookieUtils;
import static ru.yandex.autotests.morda.utils.cookie.MordaCookieUtils.YANDEXUID;
import static ru.yandex.autotests.morda.utils.matchers.AllOfDetailedMatcher.allOfDetailed;
import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.autotests.mordacommonsteps.matchers.RegexMatcher.matches;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.HREF;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;
import static ru.yandex.qatools.htmlelements.matchers.WrapsElementMatchers.hasText;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 23/04/15
 */
@Name("Авторизованный хедер")
@FindBy(xpath = "//div[contains(@class, 'personal')]")
public class HeaderAuthorized extends HtmlElement implements Validateable<DesktopYaruMorda> {

    @Name("Имя пользователя")
    @FindBy(xpath = ".//a[contains(@class, 'personal__link')]")
    private HtmlElement username;

    @Name("Ссылка в почту")
    @FindBy(xpath = ".//a[contains(@class, 'personal__mail')]")
    private HtmlElement mailLink;

    @Name("Ссылка \"Выход\"")
    @FindBy(xpath = ".//a[contains(@class, 'personal__exit')]")
    private HtmlElement exitLink;

    @Override
    public HierarchicalErrorCollector validate(Validator<? extends DesktopYaruMorda> validator) {
        return collector()
                .check(shouldSeeElement(this))
                .check(
                        validateUsername(validator),
                        validateMailLink(validator),
                        validateExitLink(validator)
                );
    }

    @Step("Check username")
    public HierarchicalErrorCollector validateUsername(Validator<? extends DesktopYaruMorda> validator) {
        DesktopYaruMorda morda = validator.getMorda();
        return collector()
                .check(shouldSeeElement(username))
                .check(shouldSeeElementMatchingTo(username, allOfDetailed(
                        hasText(validator.getUser().getLogin()),
                        hasAttribute(HREF, equalTo(
                                fromUri(morda.getPassportUrl())
                                        .path("passport")
                                        .queryParam("mode", "passport").build().toString()
                        ))
                )));
    }

    @Step("Check mail link")
    public HierarchicalErrorCollector validateMailLink(Validator<? extends DesktopYaruMorda> validator) {
        return collector()
                .check(shouldSeeElement(mailLink))
                .check(shouldSeeElementMatchingTo(mailLink, allOfDetailed(
                        hasText(matches(getTranslation(Dictionary.Home.Mail.TITLE, validator.getMorda().getLanguage()) + "  \\d+")),
                        hasAttribute(HREF, startsWith("https://mail.yandex.ru"))
                )));
    }

    @Step("Check exit link")
    public HierarchicalErrorCollector validateExitLink(Validator<? extends DesktopYaruMorda> validator) {
        DesktopYaruMorda morda = validator.getMorda();
        WebDriverCookieUtils cookieUtils = cookieUtils(validator.getDriver());
        Cookie cookie = cookieUtils.getCookieNamed(YANDEXUID, morda.getCookieDomain());

        System.out.println(cookieUtils.getCookies());
        return collector()
                .check(shouldSeeElement(exitLink))
                .check(shouldSeeElementMatchingTo(exitLink, allOfDetailed(
                        hasText(matches(getTranslation(Dictionary.Home.Mail.LOGOUT, validator.getMorda().getLanguage()))),
                        hasAttribute(HREF, startsWith(
                                fromUri(morda.getPassportUrl())
                                        .path("passport")
                                        .queryParam("mode", "logout")
                                        .queryParam("yu", "")
                                        .build().toString()
                        ))
                )));
    }
}
