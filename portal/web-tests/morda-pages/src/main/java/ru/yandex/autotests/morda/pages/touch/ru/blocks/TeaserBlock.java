package ru.yandex.autotests.morda.pages.touch.ru.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validateable;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validator;
import ru.yandex.autotests.morda.pages.touch.ru.TouchRuMorda;
import ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector;
import ru.yandex.autotests.mordabackend.beans.bannerdebug.BannerImg;
import ru.yandex.autotests.mordabackend.beans.bannerdebug.Teaser;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import java.util.Optional;

import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.isEmptyOrNullString;
import static ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector.collector;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElement;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElementMatchingTo;
import static ru.yandex.autotests.morda.utils.matchers.AllOfDetailedMatcher.allOfDetailed;
import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.HEIGHT;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.HREF;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.SRC;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.WIDTH;
import static ru.yandex.qatools.htmlelements.matchers.WrapsElementMatchers.hasText;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 19/05/15
 */
@Name("Тизер")
@FindBy(xpath = "//div[contains(@class,'teaser_type_general')]")
public class TeaserBlock extends HtmlElement implements Validateable<TouchRuMorda> {

    @Name("Иконка тизера")
    @FindBy(xpath = ".//img[contains(@class, 'teaser__img')]")
    private HtmlElement teaserIcon;

    @Name("Ссылка иконки тизера")
    @FindBy(xpath = ".//a[.//img[contains(@class, 'teaser__img')]]")
    private HtmlElement teaserIconLink;

    @Name("Ссылка тизера")
    @FindBy(xpath = ".//a[contains(@class, 'teaser__text-link')]")
    private HtmlElement teaserLink;

    @Name("Возрастное ограничение тизера")
    @FindBy(xpath = ".//span[contains(@class, 'teaser__age')]")
    private HtmlElement teaserAge;

    private TeaserServiceBlock serviceTypeTeaser;

    @Override
    @Step("Check teaser")
    public HierarchicalErrorCollector validate(Validator<? extends TouchRuMorda> validator) {
        HierarchicalErrorCollector collector = collector();

        Optional<Teaser> teaser = Optional.ofNullable(
                validator.getCleanvars().getBannerDebug().getBanners().getTeaser());

        teaser.ifPresent(e ->
                collector
                .check(shouldSeeElement(this))
                .check(
                        validateTeaserIcon(validator),
                        validateTeaserText(validator)
                ));

        return collector;
    }

    @Step("Check teaser icon")
    public HierarchicalErrorCollector validateTeaserIcon(Validator<? extends TouchRuMorda> validator) {
        Teaser teaser = validator.getCleanvars().getBannerDebug().getBanners().getTeaser();
        BannerImg teaserImg = teaser.getImg();
        return collector()
                .check(
                        collector()
                                .check(shouldSeeElement(teaserIcon))
                                .check(
                                        shouldSeeElementMatchingTo(teaserIcon, allOfDetailed(
                                                hasAttribute(SRC, equalTo(teaserImg.getUrl())),
                                                hasAttribute(WIDTH, equalTo("57")),
                                                hasAttribute(HEIGHT, equalTo("57"))
                                        ))
                                ),
                        collector()
                                .check(shouldSeeElement(teaserIconLink))
                                .check(
                                        shouldSeeElementMatchingTo(teaserIconLink, allOfDetailed(
                                                        hasAttribute(HREF, equalTo(teaser.getUrl1())))
                                        )

                                )
                );

    }

    @Step("Check teaser text")
    public HierarchicalErrorCollector validateTeaserText(Validator<? extends TouchRuMorda> validator) {

        Teaser teaser = validator.getCleanvars().getBannerDebug().getBanners().getTeaser();

        HierarchicalErrorCollector collector = collector()
                .check(
                        collector()
                                .check(shouldSeeElement(teaserLink))
                                .check(
                                        shouldSeeElementMatchingTo(teaserLink, allOfDetailed(
                                                        hasText(equalTo(teaser.getText1())),
                                                        hasAttribute(HREF, equalTo(teaser.getUrl1())))
                                        )
                                )

                );

        if (!isEmptyOrNullString().matches(teaser.getAgeRestriction())) {
            collector.check(
                    collector()
                            .check(shouldSeeElement(teaserAge))
                            .check(
                                    shouldSeeElementMatchingTo(teaserAge, hasText(teaser.getAgeRestriction()))
                            )
            );
        }

        return collector;
    }

}
