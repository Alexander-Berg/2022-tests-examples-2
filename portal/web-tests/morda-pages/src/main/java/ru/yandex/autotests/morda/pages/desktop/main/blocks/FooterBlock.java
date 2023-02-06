package ru.yandex.autotests.morda.pages.desktop.main.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.morda.pages.desktop.main.DesktopMainMorda;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validateable;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validator;
import ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector;
import ru.yandex.autotests.mordabackend.beans.miniservices.Direct;
import ru.yandex.autotests.mordabackend.beans.miniservices.Metrika;
import ru.yandex.autotests.utils.morda.url.Domain;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import static java.lang.String.format;
import static javax.ws.rs.core.UriBuilder.fromUri;
import static org.hamcrest.Matchers.anyOf;
import static org.hamcrest.Matchers.endsWith;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.startsWith;
import static ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector.collector;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElement;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElementMatchingTo;
import static ru.yandex.autotests.morda.steps.CheckSteps.url;
import static ru.yandex.autotests.morda.utils.matchers.AllOfDetailedMatcher.allOfDetailed;
import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.HREF;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Business.ADV;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Business.DIRECT;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Business.METRIKA;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Foot.BLOG;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Foot.COMPANY_NOM;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Foot.FOOT_VACANCIES;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;
import static ru.yandex.autotests.utils.morda.url.Domain.RU;
import static ru.yandex.autotests.utils.morda.url.Domain.UA;
import static ru.yandex.qatools.htmlelements.matchers.WrapsElementMatchers.hasText;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 01/04/15
 */
@Name("Футер")
@FindBy(xpath = "//div[contains(@class, 'col') and contains(@class, 'footer')]")
public class FooterBlock extends HtmlElement implements Validateable<DesktopMainMorda> {

    public FooterBusinessBlock businessBlock;
    public FooterCompanyBlock companyBlock;

    @Override
    @Step("Check footer")
    public HierarchicalErrorCollector validate(Validator<? extends DesktopMainMorda> validator) {
        return collector()
                .check(shouldSeeElement(this))
                .check(
                        businessBlock.validate(validator),
                        companyBlock.validate(validator)
                );
    }

    @Name("Бизнес-блок")
    @FindBy(xpath = "//div[contains(@class, 'foot__business')]")
    public static class FooterBusinessBlock extends HtmlElement implements Validateable<DesktopMainMorda> {

        @Name("Ссылка \"Директ\"")
        @FindBy(xpath = ".//a[1]")
        public HtmlElement direct;

        @Name("Подпись \"Директ\"")
        @FindBy(xpath = ".//a[2]")
        public HtmlElement directSublink;

        @Name("Ссылка \"Метрика\"")
        @FindBy(xpath = ".//a[3]")
        public HtmlElement metrika;

        @Name("Ссылка \"Реклама\"")
        @FindBy(xpath = ".//a[4]")
        public HtmlElement adv;

        @Name("Ссылка \"Яндекс по умолчанию\"")
        @FindBy(xpath = ".//a[5]")
        public HtmlElement yandexDefault;

        @Step("{0}")
        public static HierarchicalErrorCollector validateDirect(HtmlElement direct, Validator<? extends DesktopMainMorda> validator) {
            Direct directData = validator.getCleanvars().getMiniservices().getDirect();
            return collector()
                    .check(shouldSeeElement(direct))
                    .check(
                            shouldSeeElementMatchingTo(direct, allOfDetailed(
                                    hasText(getTranslation(DIRECT, validator.getMorda().getLanguage())),
                                    hasAttribute(HREF, equalTo(url(directData.getHref(), validator.getMorda().getScheme())))
                            ))
                    );
        }

        @Step("{0}")
        public static HierarchicalErrorCollector validateDirectSublink(HtmlElement directSublink, Validator<? extends DesktopMainMorda> validator) {
            Direct directData = validator.getCleanvars().getMiniservices().getDirect();
            return collector()
                    .check(shouldSeeElement(directSublink))
                    .check(
                            shouldSeeElementMatchingTo(directSublink, allOfDetailed(
                                    hasText(directData.getSubtitle()),
                                    hasAttribute(HREF, equalTo(url(directData.getSubhref().replaceAll("&amp;", "&"), validator.getMorda().getScheme())))
                            ))
                    );
        }

        @Step("{0}")
        public static HierarchicalErrorCollector validateYandDefault(HtmlElement yandexDefault, Validator<? extends DesktopMainMorda> validator) {
            if(!validator.getMorda().getRegion().getDomain().equals(Domain.RU)){
                return collector();
            }
            return collector()
                    .check(shouldSeeElement(yandexDefault))
                    .check(
                            shouldSeeElementMatchingTo(yandexDefault, allOfDetailed(
//                                    hasText(getTranslation("home","business","switchToYandex", validator.getMorda().getLanguage())),
                                    hasText("Яндекс по умолчанию"),
                                    hasAttribute(HREF, anyOf(
                                            startsWith("https://yandex.ru/set"),
                                            equalTo("https://set.yandex.ru/")))
                            ))
                    );
        }

        @Step("{0}")
        public static HierarchicalErrorCollector validateMetrika(HtmlElement metrika, Validator<? extends DesktopMainMorda> validator) {
            Metrika metrikaData = validator.getCleanvars().getMiniservices().getMetrika();
            return collector()
                    .check(shouldSeeElement(metrika))
                    .check(
                            shouldSeeElementMatchingTo(metrika, allOfDetailed(
                                    hasText(getTranslation(METRIKA, validator.getMorda().getLanguage())),
                                    hasAttribute(HREF, equalTo(url(metrikaData.getHref(), validator.getMorda().getScheme())))
                            ))
                    );
        }

        @Step("{0}")
        public static HierarchicalErrorCollector validateAdv(HtmlElement adv, Validator<? extends DesktopMainMorda> validator) {

            String href = fromUri(validator.getMorda().getUrl())
                    .path("/adv/")
                    .replaceQuery("from=main_bottom")
                    .build()
                    .toString();

            return collector()
                    .check(shouldSeeElement(adv))
                    .check(
                            shouldSeeElementMatchingTo(adv, allOfDetailed(
                                    hasText(getTranslation(ADV, validator.getMorda().getLanguage())),
                                    hasAttribute(HREF, equalTo(href))
                            ))
                    );
        }

        @Override
        @Step("Check footer business block")
        public HierarchicalErrorCollector validate(Validator<? extends DesktopMainMorda> validator) {
            return collector()
                    .check(shouldSeeElement(this))
                    .check(
                            validateDirect(direct, validator),
                            validateDirectSublink(directSublink, validator),
                            validateMetrika(metrika, validator),
                            validateAdv(adv, validator)
//                            validateYandDefault(yandexDefault, validator)

                    );
        }
    }

    @Name("Блок компании")
    @FindBy(xpath = "//div[contains(@class, 'foot__company-links')]")
    public static class FooterCompanyBlock extends HtmlElement implements Validateable<DesktopMainMorda> {

        @Name("Ссылка \"Help\"")
        @FindBy(xpath = ".//a[contains(@class, 'company-links__help')]")
        public HtmlElement help;

        @Name("Ссылка \"Feedback\"")
        @FindBy(xpath = ".//a[contains(@class, 'company-links__feedback')]")
        public HtmlElement feedback;

        @Name("Ссылка \"Вакансии\"")
        @FindBy(xpath = ".//a[3]")
        public HtmlElement jobs;

        @Name("Ссылка \"Блог\"")
        @FindBy(xpath = ".//a[4]")
        public HtmlElement blog;

        @Name("Ссылка \"Компания\"")
        @FindBy(xpath = ".//a[5]")
        public HtmlElement company;

        @Name("Ссылка \"About\"")
        @FindBy(xpath = ".//a[6]")
        public HtmlElement about;

        @Step("{0}")
        public static HierarchicalErrorCollector validateHelp(HtmlElement help, Validator<? extends DesktopMainMorda> validator) {
            Domain domain = validator.getMorda().getRegion().getDomain().equals(UA) ? UA : RU;
            String href = format("https://yandex%s/support/", domain);

            return collector()
                    .check(shouldSeeElement(help))
                    .check(
                            shouldSeeElementMatchingTo(help, hasAttribute(HREF, equalTo(href)))
                    );
        }

        @Step("{0}")
        public static HierarchicalErrorCollector validateFeedback(HtmlElement feedback, Validator<? extends DesktopMainMorda> validator) {
            String href = format("%s://feedback2.yandex%s/default/", validator.getMorda().getScheme(),
                    validator.getMorda().getRegion().getDomain());
            return collector()
                    .check(shouldSeeElement(feedback))
                    .check(
                            shouldSeeElementMatchingTo(feedback, hasAttribute(HREF, equalTo(href)))
                    );
        }

        @Step("{0}")
        public static HierarchicalErrorCollector validateJobs(HtmlElement jobs, Validator<? extends DesktopMainMorda> validator) {
            Domain domain = validator.getMorda().getRegion().getDomain().equals(UA) ? UA : RU;
            String href = format("https://yandex%s/jobs", domain);

            return collector()
                    .check(shouldSeeElement(jobs))
                    .check(
                            shouldSeeElementMatchingTo(jobs, allOfDetailed(
                                    hasText(getTranslation(FOOT_VACANCIES, validator.getMorda().getLanguage())),
                                    hasAttribute(HREF, equalTo(href))
                            ))
                    );
        }

        @Step("{0}")
        public static HierarchicalErrorCollector validateBlog(HtmlElement blog, Validator<? extends DesktopMainMorda> validator) {
            Domain domain = validator.getMorda().getRegion().getDomain().equals(UA) ? UA : RU;
            String href = format("https://yandex%s/blog/company/", domain);

            return collector()
                    .check(shouldSeeElement(blog))
                    .check(
                            shouldSeeElementMatchingTo(blog, allOfDetailed(
                                    hasText(getTranslation(BLOG, validator.getMorda().getLanguage())),
                                    hasAttribute(HREF, equalTo(href))
                            ))
                    );
        }

        @Step("{0}")
        public static HierarchicalErrorCollector validateCompany(HtmlElement company, Validator<? extends DesktopMainMorda> validator) {
            Domain domain = validator.getMorda().getRegion().getDomain().equals(UA) ? UA : RU;
            String href = format("https://yandex%s/company/", domain);

            return collector()
                    .check(shouldSeeElement(company))
                    .check(
                            shouldSeeElementMatchingTo(company, allOfDetailed(
                                    hasText(getTranslation(COMPANY_NOM, validator.getMorda().getLanguage())),
                                    hasAttribute(HREF, equalTo(href))
                            ))
                    );
        }

        @Step("{0}")
        public static HierarchicalErrorCollector validateAbout(HtmlElement about, Validator<? extends DesktopMainMorda> validator) {
            return collector()
                    .check(shouldSeeElement(about))
                    .check(
                            shouldSeeElementMatchingTo(about, allOfDetailed(
                                    hasText("About"),
                                    hasAttribute(HREF, equalTo("https://yandex.com/company/"))
                            ))
                    );
        }

        @Override
        public HierarchicalErrorCollector validate(Validator<? extends DesktopMainMorda> validator) {
            HierarchicalErrorCollector copyright = collector()
                    .check(shouldSeeElementMatchingTo(this, hasText(endsWith("© Яндекс"))));

            return collector()
                    .check(shouldSeeElement(this))
                    .check(
                            copyright,
                            validateHelp(help, validator),
                            validateFeedback(feedback, validator),
                            validateJobs(jobs, validator),
                            validateBlog(blog, validator),
                            validateCompany(company, validator),
                            validateAbout(about, validator)
                    );
        }
    }
}
