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
import java.util.List;

import static ch.lambdaj.Lambda.convert;
import static ch.lambdaj.Lambda.extract;
import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.on;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.hasSize;
import static org.junit.Assume.assumeThat;
import static ru.yandex.autotests.mordabackend.blocks.CleanvarsBlock.LANGUAGE;
import static ru.yandex.autotests.mordabackend.blocks.CleanvarsBlock.LANGUAGECHOOSERINFOOTER;
import static ru.yandex.autotests.mordabackend.blocks.CleanvarsBlock.LANGUAGE_LC;
import static ru.yandex.autotests.mordabackend.language.LanguageUtils.LANGUAGE_REGIONS_ALL;
import static ru.yandex.autotests.mordabackend.language.LanguageUtils.getDefaultLanguage;
import static ru.yandex.autotests.mordabackend.language.LanguageUtils.getDefaultRegionLanguages;
import static ru.yandex.autotests.mordabackend.useragents.UserAgent.FF_34;
import static ru.yandex.autotests.mordabackend.useragents.UserAgent.PDA;
import static ru.yandex.autotests.mordabackend.useragents.UserAgent.TOUCH;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.shouldHaveParameter;
import static ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils.parameters;
import static ru.yandex.qatools.matchers.collection.HasSameItemsAsListMatcher.hasSameItemsAsList;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 29.07.14
 */
@Aqua.Test(title = "Default Language")
@Features("Language")
@Stories("Default Language")
@RunWith(CleanvarsParametrizedRunner.class)
public class DefaultLanguageTest {

    @CleanvarsParametrizedRunner.Parameters("{3}, {4}")
    public static ParametersUtils parameters =
            parameters(LANGUAGE_REGIONS_ALL)
                    .withUserAgents(FF_34, PDA, TOUCH)
                    .withCleanvarsBlocks(LANGUAGE, LANGUAGE_LC, LANGUAGECHOOSERINFOOTER);

    private Client client;
    private UserAgent userAgent;
    private Cleanvars cleanvars;
    private Region region;

    public DefaultLanguageTest(MordaClient mordaClient, Client client, Cleanvars cleanvars,
                               Region region, UserAgent userAgent) {
        this.client = client;
        this.userAgent = userAgent;
        this.cleanvars = cleanvars;
        this.region = region;
    }

    @Test
    public void defaultLanguage() {
        shouldHaveParameter(cleanvars.getLanguage(),
                having(on(String.class),
                        equalTo(getDefaultLanguage(region, userAgent).getExportValue().toUpperCase())));
    }

    @Test
    public void defaultLanguageLc() {
        shouldHaveParameter(cleanvars.getLanguageLc(),
                having(on(String.class),
                        equalTo(getDefaultLanguage(region, userAgent).getExportValue().toLowerCase())));
    }

    @Test
    public void defaultLanguagesPopupSize() {
        assumeThat("Проверяем только на десктопе", userAgent, equalTo(FF_34));
        shouldHaveParameter(cleanvars.getLanguageChooserInFooter(), cleanvars.getLanguageChooserInFooter(),
                hasSize(getDefaultRegionLanguages(region).size()));
    }

    @Test
    public void defaultLanguagesPopup() {
        assumeThat("Проверяем только на десктопе", userAgent, equalTo(FF_34));
        List<String> actualLanguages = extract(cleanvars.getLanguageChooserInFooter(),
                on(LanguageChooserInFooter.class).getLang());
        List<String> expectedLanguages = convert(getDefaultRegionLanguages(region), new Converter<Language, String>() {
            @Override
            public String convert(Language from) {
                return from.getValue();
            }
        });
        shouldHaveParameter(cleanvars.getLanguageChooserInFooter(), actualLanguages,
                hasSameItemsAsList(expectedLanguages));
    }
}
