package ru.yandex.autotests.morda.pages.desktop.main.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.morda.pages.desktop.main.DesktopMainMorda;
import ru.yandex.autotests.morda.pages.desktop.main.htmlelements.ImageLink;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validateable;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validator;
import ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector;
import ru.yandex.autotests.mordabackend.beans.bannerdebug.Teaser;
import ru.yandex.autotests.mordabackend.beans.teaser.AtomTeaser;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import java.util.function.Function;

import static java.lang.String.valueOf;
import static org.hamcrest.Matchers.allOf;
import static org.hamcrest.Matchers.endsWith;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.startsWith;
import static ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector.collector;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldNotSeeElement;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElement;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElementMatchingTo;
import static ru.yandex.autotests.morda.steps.CheckSteps.url;
import static ru.yandex.autotests.morda.utils.matchers.AllOfDetailedMatcher.allOfDetailed;
import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.HEIGHT;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.HREF;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.SRC;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.WIDTH;
import static ru.yandex.qatools.htmlelements.matchers.WrapsElementMatchers.hasText;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 26/02/15
 */
@Name("Тизер")
@FindBy(xpath = "//div[contains(@class, 'teaser__content')]")
public class TeaserBlock extends HtmlElement implements Validateable<DesktopMainMorda> {

    @Name("Заголовок тизера")
    @FindBy(xpath = ".//h1[contains(@class, 'title')]/a")
    public HtmlElement title;

    @Name("Картинка тизера")
    @FindBy(xpath = ".//a[./img]")
    public ImageLink teaserImage;

    @Name("Подпись тизера")
    @FindBy(xpath = ".//div[contains(@class, 'description')]")
    public HtmlElement description;

    @Step("{0}")
    public static HierarchicalErrorCollector validateTitle(HtmlElement title, Validator<? extends DesktopMainMorda> validator) {

        AtomTeaser atomTeaser = validator.getCleanvars().getTeaser();

        String titleUrl;
        String titleText1;
        String titleText2;

        Function<String, String> normalizeTitle = (s) -> s.trim()
                .replace("&mdash;", "—")
                .replaceAll("  ", " ")
                .replaceAll(" ", " ");

        if (atomTeaser.getValue() == null) {
            Teaser teaserData = validator.getCleanvars().getBannerDebug().getBanners().getTeaser();
            titleText1 =  normalizeTitle.apply(teaserData.getTitle1());
            titleText2 = normalizeTitle.apply(teaserData.getTitle2());
            titleUrl = teaserData.getUrl();
        } else {
            titleText1 = normalizeTitle.apply(atomTeaser.getValue().getTitle1());
            titleText2 = normalizeTitle.apply(atomTeaser.getValue().getTitle2());
            titleUrl = atomTeaser.getValue().getUrl();
        }
        return collector()
                .check(shouldSeeElement(title))
                .check(
                        shouldSeeElementMatchingTo(title, allOfDetailed(
                                hasText(allOf(startsWith(titleText1), endsWith(titleText2))),
                                hasAttribute(HREF,
                                        equalTo(url(titleUrl, validator.getMorda().getScheme()))
                                )
                        ))
                );
    }

    @Step("{0}")
    public static HierarchicalErrorCollector validateImage(ImageLink teaserImage, Validator<? extends DesktopMainMorda> validator) {

        AtomTeaser atomTeaser = validator.getCleanvars().getTeaser();

        String imageUrl;
        String width;
        String height;
        String srcUrl;

        if (atomTeaser.getValue() == null) {
            Teaser teaserData = validator.getCleanvars().getBannerDebug().getBanners().getTeaser();
            imageUrl = teaserData.getUrl();
            width = valueOf(teaserData.getImg().getWidth());
            height = valueOf(teaserData.getImg().getHeight());
            srcUrl = teaserData.getImg().getUrl();
        } else {
            imageUrl = atomTeaser.getValue().getUrl();
            width = atomTeaser.getValue().getImg().getWidth();
            height = atomTeaser.getValue().getImg().getHeight();
            srcUrl = atomTeaser.getValue().getImg().getUrl();
        }

        return collector()
                .check(shouldSeeElement(teaserImage))
                .check(
                        shouldSeeElementMatchingTo(teaserImage,
                                hasAttribute(HREF, equalTo(url(imageUrl, validator.getMorda().getScheme())))
                        ),
                        shouldSeeElementMatchingTo(teaserImage.img, allOfDetailed(
                                hasAttribute(WIDTH, equalTo(width)),
                                hasAttribute(HEIGHT, equalTo(height)),
                                hasAttribute(SRC, equalTo(url(srcUrl, validator.getMorda().getScheme())))
                        ))
                );
    }

    @Step("{0}")
    public static HierarchicalErrorCollector validateDescription(HtmlElement description, Validator<? extends DesktopMainMorda> validator) {

        AtomTeaser atomTeaser = validator.getCleanvars().getTeaser();

        String descriptionText;

        if (atomTeaser.getValue() == null) {
            Teaser teaserData = validator.getCleanvars().getBannerDebug().getBanners().getTeaser();
            descriptionText = (teaserData.getText1().trim() + " " + teaserData.getText2().trim()).trim();
        } else {
            descriptionText = (atomTeaser.getValue().getText1().trim() + " " + atomTeaser.getValue().getText2().trim())
                    .trim();
        }

        if (descriptionText.isEmpty()) {
            return collector()
                    .check(shouldNotSeeElement(description));
        }
        return collector()
                .check(shouldSeeElement(description))
                .check(
                        shouldSeeElementMatchingTo(description, hasText(descriptionText))
                );
    }

    @Override
    public HierarchicalErrorCollector validate(Validator<? extends DesktopMainMorda> validator) {
        return collector()
                .check(shouldSeeElement(this))
                .check(
                        validateTitle(title, validator),
                        validateImage(teaserImage, validator),
                        validateDescription(description, validator)
                );
    }
}
