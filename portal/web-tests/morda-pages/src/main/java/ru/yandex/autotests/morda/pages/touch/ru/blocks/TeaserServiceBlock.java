package ru.yandex.autotests.morda.pages.touch.ru.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validateable;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validator;
import ru.yandex.autotests.morda.pages.touch.ru.TouchRuMorda;
import ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector;
import ru.yandex.autotests.mordabackend.beans.teaser_service.TeaserService;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import java.util.Optional;

import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector.collector;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElement;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElementMatchingTo;
import static ru.yandex.autotests.morda.utils.matchers.AllOfDetailedMatcher.allOfDetailed;
import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.HREF;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;
import static ru.yandex.qatools.htmlelements.matchers.WrapsElementMatchers.hasText;

/**
 * @author Ivan Nikolaev <ivannik@yandex-team.ru>
 */
@Name("Цветной тизер")
@FindBy(xpath = "//div[contains(@class, 'teaser_type_service')]")
public class TeaserServiceBlock extends HtmlElement implements Validateable<TouchRuMorda> {

    @Name("Верхняя часть цветного тизера")
    @FindBy(xpath = ".//a[contains(@class, 'teaser__service-up-link')]")
    private HtmlElement teaserUpLink;

    @Name("Нижняя часть цветного тизера")
    @FindBy(xpath = ".//a[contains(@class, 'teaser__service-down-link')]")
    private HtmlElement teaserDownLink;

    @Name("Иконка цветного тизера")
    @FindBy(xpath = ".//div[contains(@class, 'teaser__service-up-icon')]")
    private HtmlElement teaserIcon;

    @Name("Заголовок цветного тизера")
    @FindBy(xpath = ".//div[contains(@class, 'teaser__service-up-title')]")
    private HtmlElement teaserTitle;

    @Name("Текст цветного тизера")
    @FindBy(xpath = ".//div[@class='teaser__service-up-text']")
    private HtmlElement teaserText;

    @Name("Возрастное ограничение цветного тизера")
    @FindBy(xpath = ".//div[contains(@class, 'teaser__service-up-age')]")
    private HtmlElement teaserAge;

    @Override
    @Step("Check service type teaser")
    public HierarchicalErrorCollector validate(Validator<? extends TouchRuMorda> validator) {
        HierarchicalErrorCollector collector = collector();

        Optional.ofNullable(validator.getCleanvars().getTeaserService().getUrl()).ifPresent(url ->
                        collector
                                .check(shouldSeeElement(this))
                                .check(
                                        validateTeaserUpLink(validator),
                                        validateTeaserDownLink(validator)
                                )
        );

        return collector;
    }

    @Step("Check up teaser part")
    public HierarchicalErrorCollector validateTeaserUpLink(Validator<? extends TouchRuMorda> validator) {

        TeaserService teaserService = validator.getCleanvars().getTeaserService();
        HierarchicalErrorCollector collector = collector()
                .check(shouldSeeElement(teaserUpLink))
                .check(
                        collector()
                                .check(
                                        shouldSeeElementMatchingTo(teaserUpLink, allOfDetailed(
                                                        hasAttribute(HREF, equalTo(teaserService.getUrl())))
                                        )
                                ),
                        collector()
                                .check(shouldSeeElement(teaserIcon)),
                        collector()
                                .check(shouldSeeElement(teaserTitle))
                                .check(
                                        shouldSeeElementMatchingTo(teaserTitle, allOfDetailed(
                                                hasText(teaserService.getTitle())
                                        ))

                                ),
                        collector()
                                .check(shouldSeeElement(teaserText))
                                .check(
                                        shouldSeeElementMatchingTo(teaserText, allOfDetailed(
                                                hasText(teaserService.getText())
                                        ))

                                )
                );

        if (validator.getCleanvars().getIsRussia() == 1) {
            collector.check(
                    collector()
                            .check(shouldSeeElement(teaserAge))
                            .check(
                                    shouldSeeElementMatchingTo(teaserAge, hasText("0+"))
                            )
            );
        }

        return collector;

    }

    @Step("Check down teaser part")
    public HierarchicalErrorCollector validateTeaserDownLink(Validator<? extends TouchRuMorda> validator) {
        TeaserService teaserService = validator.getCleanvars().getTeaserService();
        String devicePlatform = validator.getCleanvars().getDevicePlatform();
        return collector()
                .check(shouldSeeElement(teaserDownLink))
                .check(
                        shouldSeeElementMatchingTo(teaserDownLink, allOfDetailed(
                                        hasText(getTranslation("home", "teaser",
                                                "download." + devicePlatform, validator.getMorda().getLanguage()).replace("  ", " ")),
                                        hasAttribute(HREF, equalTo(teaserService.getUrl())))
                        )
                );

    }

}
