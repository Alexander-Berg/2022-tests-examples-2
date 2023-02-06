package ru.yandex.autotests.morda.pages.touch.ru.blocks;

import org.hamcrest.Matcher;
import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validateable;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validator;
import ru.yandex.autotests.morda.pages.touch.ru.TouchRuMorda;
import ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector;
import ru.yandex.autotests.mordabackend.beans.servicesmobile.ServiceMobileItem;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import java.util.List;

import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector.collector;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElement;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElementMatchingTo;
import static ru.yandex.autotests.morda.steps.CheckSteps.url;
import static ru.yandex.autotests.morda.utils.matchers.AllOfDetailedMatcher.allOfDetailed;
import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.HREF;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Mobile.FOOT_ALL;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Mobile.FOOT_FEEDBACK;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Mobile.FOOT_TUNE;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Mobile.HEAD_ENTER;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;
import static ru.yandex.qatools.htmlelements.matchers.WrapsElementMatchers.hasText;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 01/04/15
 */
@Name("Боковое меню")
@FindBy(xpath = "//div[contains(@class, 'menu2__list')]")
public class MenuBlock extends HtmlElement implements Validateable<TouchRuMorda> {

    @FindBy(xpath = "//body")
    private HtmlElement body;

    @Name("Заголовок меню")
    @FindBy(xpath = ".//div[contains(@class, 'title')]")
    public HtmlElement title;

    @Name("табы ")
    @FindBy(xpath = ".//a")
    public List<HtmlElement> allLinks;

    @Override
    public boolean isDisplayed() {
        return body.getAttribute("class").contains("body_menu_shown");
    }

    @Step("{0}")
    public static HierarchicalErrorCollector validateMenuLink(HtmlElement link,
                                                              Matcher<String> textMatcher,
                                                              Matcher<String> hrefMatcher,
                                                              Validator<? extends TouchRuMorda> validator) {
        return collector()
                .check(shouldSeeElement(link))
                .check(
                        shouldSeeElementMatchingTo(link, allOfDetailed(
                                hasText(textMatcher),
                                hasAttribute(HREF, hrefMatcher)
                        ))
                );
    }

    @Override
    public HierarchicalErrorCollector validate(Validator<? extends TouchRuMorda> validator) {
        List<ServiceMobileItem> servicesMobileData = validator.getCleanvars().getServicesMobile().getListMore();
        HierarchicalErrorCollector collector = collector();

        int i = 0;
        for (ServiceMobileItem item : servicesMobileData) {
            collector.check(
                    validateMenuLink(
                            allLinks.get(i++),
                            equalTo(getTranslation("home", "tabs", item.getId(), validator.getMorda().getLanguage())),
                            equalTo(url(item.getUrl(), validator.getMorda().getScheme())),
                            validator
                    )
            );
        }
        collector.check(
                validateMenuLink(
                        allLinks.get(i++),
                        equalTo(getTranslation(FOOT_ALL, validator.getMorda().getLanguage())),
                        equalTo(validator.getMorda().getUrl() + "all"),
                        validator
                )
        );
        collector.check(
                validateMenuLink(
                        allLinks.get(i++),
                        equalTo(getTranslation(HEAD_ENTER, validator.getMorda().getLanguage())),
                        equalTo(servicesMobileData.get(2).getHref()),
                        validator
                )
        );
        collector.check(
                validateMenuLink(
                        allLinks.get(i++),
                        equalTo(getTranslation(FOOT_TUNE, validator.getMorda().getLanguage())),
                        equalTo(validator.getCleanvars().getSetupPages().getAll().replace("&amp;", "&")),
                        validator
                )
        );
        collector.check(
                validateMenuLink(
                        allLinks.get(i),
                        equalTo(getTranslation(FOOT_FEEDBACK, validator.getMorda().getLanguage())),
                        equalTo("http://mobile-feedback.yandex.ru/?from=m-mainpage"),
                        validator
                )
        );

        return collector;
    }
}
