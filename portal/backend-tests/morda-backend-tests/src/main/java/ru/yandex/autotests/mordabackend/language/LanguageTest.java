package ru.yandex.autotests.mordabackend.language;

import ch.lambdaj.function.convert.Converter;
import org.junit.Test;
import org.junit.runner.RunWith;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mordabackend.MordaClient;
import ru.yandex.autotests.mordabackend.beans.cleanvars.Cleanvars;
import ru.yandex.autotests.mordabackend.beans.languagechooser.LanguageChooserInFooter;
import ru.yandex.autotests.mordabackend.useragents.UserAgent;
import ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils;
import ru.yandex.autotests.mordabackend.utils.runner.CleanvarsParametrizedRunner;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import javax.ws.rs.client.Client;
import java.io.IOException;
import java.util.List;

import static ch.lambdaj.Lambda.convert;
import static ch.lambdaj.Lambda.extract;
import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.on;
import static ch.lambdaj.Lambda.select;
import static ch.lambdaj.Lambda.selectFirst;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.hasSize;
import static org.hamcrest.Matchers.notNullValue;
import static org.junit.Assume.assumeThat;
import static ru.yandex.autotests.mordabackend.blocks.CleanvarsBlock.HOMEPAGENOARGS;
import static ru.yandex.autotests.mordabackend.blocks.CleanvarsBlock.LANGUAGE;
import static ru.yandex.autotests.mordabackend.blocks.CleanvarsBlock.LANGUAGECHOOSERINFOOTER;
import static ru.yandex.autotests.mordabackend.blocks.CleanvarsBlock.LANGUAGE_LC;
import static ru.yandex.autotests.mordabackend.blocks.CleanvarsBlock.SK;
import static ru.yandex.autotests.mordabackend.language.LanguageUtils.LANGUAGE_REGIONS_MAIN;
import static ru.yandex.autotests.mordabackend.language.LanguageUtils.getLangHrefMatcher;
import static ru.yandex.autotests.mordabackend.language.LanguageUtils.getLangMatcher;
import static ru.yandex.autotests.mordabackend.language.LanguageUtils.getRegionLanguages;
import static ru.yandex.autotests.mordabackend.language.LanguageUtils.getSelectedLanguage;
import static ru.yandex.autotests.mordabackend.logo.LogoUtils.LANGUAGES;
import static ru.yandex.autotests.mordabackend.useragents.UserAgent.FF_34;
import static ru.yandex.autotests.mordabackend.useragents.UserAgent.PDA;
import static ru.yandex.autotests.mordabackend.useragents.UserAgent.TOUCH;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.shouldHaveParameter;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.shouldHaveResponseCode;
import static ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils.parameters;
import static ru.yandex.qatools.matchers.collection.HasSameItemsAsListMatcher.hasSameItemsAsList;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 23.07.14
 */
@Aqua.Test(title = "Current Language")
@Features("Language")
@Stories("Current Language")
@RunWith(CleanvarsParametrizedRunner.class)
public class LanguageTest {

    @CleanvarsParametrizedRunner.Parameters("{3}, {4}, {5}")
    public static ParametersUtils parameters =
            parameters(LANGUAGE_REGIONS_MAIN)
                    .withLanguages(LANGUAGES)
                    .withUserAgents(FF_34, PDA, TOUCH)
                    .withCleanvarsBlocks(LANGUAGE, LANGUAGE_LC, LANGUAGECHOOSERINFOOTER, HOMEPAGENOARGS, SK);

    private Client client;
    private Cleanvars cleanvars;
    private Region region;
    private Language language;
    private UserAgent userAgent;

    public LanguageTest(MordaClient mordaClient, Client client, Cleanvars cleanvars, Region region,
                        Language language, UserAgent userAgent) {
        this.client = client;
        this.cleanvars = cleanvars;
        this.region = region;
        this.language = language;
        this.userAgent = userAgent;
    }

    @Test
    public void languageParameter() {
        shouldHaveParameter(cleanvars.getLanguage(),
                having(on(String.class), equalTo(language.getExportValue().toUpperCase())));
    }

    @Test
    public void languageLcParameter() {
        shouldHaveParameter(cleanvars.getLanguageLc(),
                having(on(String.class), equalTo(language.getExportValue().toLowerCase())));
    }

    @Test
    public void langParameters() {
        for (LanguageChooserInFooter lang : cleanvars.getLanguageChooserInFooter()) {
            shouldHaveParameter(lang,
                    having(on(LanguageChooserInFooter.class).getLang(), getLangMatcher(lang.getLocale())));
        }
    }

    @Test
    public void langHrefParameters() throws IOException {
        for (LanguageChooserInFooter lang : cleanvars.getLanguageChooserInFooter()) {
            shouldHaveParameter(lang, having(on(LanguageChooserInFooter.class).getHref(),
                    getLangHrefMatcher(cleanvars.getHomePageNoArgs(), lang.getLang(), cleanvars.getSk())));
            shouldHaveResponseCode(client, lang.getHref(), equalTo(200));
        }
    }

    @Test
    public void languagesPopupSize() {
        assumeThat("Проверяем только на десктопе", userAgent, equalTo(FF_34));
        shouldHaveParameter(cleanvars.getLanguageChooserInFooter(), cleanvars.getLanguageChooserInFooter(),
                hasSize(getRegionLanguages(region, language).size()));
    }

    @Test
    public void languagesPopup() {
        assumeThat("Проверяем только на десктопе", userAgent, equalTo(FF_34));
        List<String> actualLanguages = extract(cleanvars.getLanguageChooserInFooter(),
                on(LanguageChooserInFooter.class).getLang());
        List<String> expectedLanguages = convert(getRegionLanguages(region, language), new Converter<Language, String>() {
            @Override
            public String convert(Language from) {
                return from.getValue();
            }
        });
        shouldHaveParameter(cleanvars.getLanguageChooserInFooter(), actualLanguages,
                hasSameItemsAsList(expectedLanguages));
    }

    @Test
    public void selectedLanguage() {
        assumeThat("Проверяем только на десктопе", userAgent, equalTo(FF_34));
        Language expected = getSelectedLanguage(region, language);
        assumeThat("Попап с выбором языка отсутствует", expected, notNullValue());
        LanguageChooserInFooter actualLanguage = selectFirst(cleanvars.getLanguageChooserInFooter(),
                having(on(LanguageChooserInFooter.class).getLang(), equalTo(expected.getValue())));
        shouldHaveParameter(actualLanguage, having(on(LanguageChooserInFooter.class).getSelected(), equalTo(1)));
        List<LanguageChooserInFooter> selected = select(cleanvars.getLanguageChooserInFooter(),
                having(on(LanguageChooserInFooter.class).getLang(), equalTo(expected.getValue())));
        shouldHaveParameter(selected, hasSize(equalTo(1)));
    }
}
