package ru.yandex.autotests.morda.pages.touch.ru.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validateable;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validator;
import ru.yandex.autotests.morda.pages.touch.ru.TouchRuMorda;
import ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector;
import ru.yandex.autotests.utils.morda.language.Dictionary;
import ru.yandex.geobase.regions.GeobaseRegion;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import java.util.List;

import static java.lang.String.format;
import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector.collector;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElement;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElementMatchingTo;
import static ru.yandex.autotests.morda.utils.matchers.AllOfDetailedMatcher.allOfDetailed;
import static ru.yandex.autotests.morda.utils.matchers.UrlMatcher.urlMatcher;
import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.HREF;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;
import static ru.yandex.qatools.htmlelements.matchers.WrapsElementMatchers.hasText;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 19/05/15
 */
@Name("Футер")
@FindBy(xpath = "//div[contains(@class, 'mfooter')]")
public class FooterBlock extends HtmlElement implements Validateable<TouchRuMorda> {

    @Name("Ссылка \"Настройка\"")
    @FindBy(xpath = ".//div[@class='mfooter__left-column']/a[1]")
    private HtmlElement settingsLink;

    @Name("Ссылка \"Все сервисы\"")
    @FindBy(xpath = ".//div[@class='mfooter__left-column']/a[2]")
    private HtmlElement allServicesLink;

    @Name("Ссылка \"Обратная связь\"")
    @FindBy(xpath = ".//div[@class='mfooter__left-column']/a[3]")
    private HtmlElement feedbackLink;

    @Name("Копирайт")
    @FindBy(xpath = ".//div[@class='mfooter__right-column']/div[1]")
    private HtmlElement copyright;

    @Name("Ссылка \"Полная версия\"")
    @FindBy(xpath = ".//div[@class='mfooter__right-column']/a")
    private HtmlElement fullVersionLink;


    @Override
    @Step("Check footer")
    public HierarchicalErrorCollector validate(Validator<? extends TouchRuMorda> validator) {
        return collector()
                .check(shouldSeeElement(this))
                .check(
                        validateSettingsLink(validator),
                        validateAllServicesLink(validator),
                        validateFeedbackLink(validator),
                        validateCopyright(validator),
                        validateFullVersionLink(validator)
                );
    }

    @Step("Check settings link")
    public HierarchicalErrorCollector validateSettingsLink(Validator<? extends TouchRuMorda> validator) {
        return collector()
                .check(
                        shouldSeeElement(settingsLink),
                        shouldSeeElementMatchingTo(settingsLink, allOfDetailed(
                                hasText(getTranslation(Dictionary.Home.Mobile.FOOT_TUNE, validator.getMorda().getLanguage())),
                                hasAttribute(HREF,
                                        equalTo(validator.getCleanvars().getSetupPages().getAll().replaceAll("&amp;", "&")))
                        ))
                );

    }

    @Step("Check all services link")
    public HierarchicalErrorCollector validateAllServicesLink(Validator<? extends TouchRuMorda> validator) {
        return collector()
                .check(
                        shouldSeeElement(allServicesLink),
                        shouldSeeElementMatchingTo(allServicesLink, allOfDetailed(
                                hasText(getTranslation(Dictionary.Home.Mobile.FOOT_ALL, validator.getMorda().getLanguage())),
                                hasAttribute(HREF, equalTo(validator.getCleanvars().getGohome() + "all"))
                        ))
                );
    }

    @Step("Check feedback link")
    public HierarchicalErrorCollector validateFeedbackLink(Validator<? extends TouchRuMorda> validator) {

        List<Integer> parents = new GeobaseRegion(validator.getMorda().getRegion().getRegionIdInt()).getParentsIds();
        int ua = 187;
        String host;

        if (parents.contains(ua)) {
            host = "yandex.ua";
        } else {
            host = "yandex.ru";
        }

        return collector()
                .check(
                        shouldSeeElement(feedbackLink),
                        shouldSeeElementMatchingTo(feedbackLink, allOfDetailed(
                                hasText(getTranslation(Dictionary.Home.Mobile.FOOT_FEEDBACK,
                                        validator.getMorda().getLanguage())),
                                hasAttribute(HREF,
                                        urlMatcher()
                                                .scheme("https")
                                                .host(host)
                                                .path("/support/common/troubleshooting/main.xml")
                                                .build())
                        ))
                );
    }

    @Step("Check copyright")
    public HierarchicalErrorCollector validateCopyright(Validator<? extends TouchRuMorda> validator) {
        return collector()
                .check(
                        shouldSeeElement(copyright),
                        shouldSeeElementMatchingTo(copyright, hasText(format("© %s %s", "2017", "Яндекс")))
                );
    }

    @Step("Check full version link")
    public HierarchicalErrorCollector validateFullVersionLink(Validator<? extends TouchRuMorda> validator) {
        return collector()
                .check(
                        shouldSeeElement(fullVersionLink),
                        shouldSeeElementMatchingTo(fullVersionLink, allOfDetailed(
                                hasText(getTranslation(Dictionary.Home.Mobile.FOOT_FULL, validator.getMorda().getLanguage())),
                                hasAttribute(HREF, equalTo(validator.getCleanvars().getSwitchType().getUrl().replaceAll("&amp;", "&")))
                                )
                        ));
    }

}