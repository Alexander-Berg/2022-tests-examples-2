package ru.yandex.autotests.mordabackend.mail;

import org.junit.Test;
import org.junit.runner.RunWith;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mordabackend.MordaClient;
import ru.yandex.autotests.mordabackend.beans.cleanvars.Cleanvars;
import ru.yandex.autotests.mordabackend.beans.mail.Mail;
import ru.yandex.autotests.mordabackend.beans.mail.PromoButton;
import ru.yandex.autotests.mordabackend.beans.mail.PromoDisk;
import ru.yandex.autotests.mordabackend.useragents.UserAgent;
import ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils;
import ru.yandex.autotests.mordabackend.utils.runner.CleanvarsParametrizedRunner;
import ru.yandex.autotests.mordaexportsclient.beans.MailPromoButtonEntry;
import ru.yandex.autotests.mordaexportsclient.beans.MailPromoDiskV12Entry;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import javax.ws.rs.client.Client;
import java.io.IOException;
import java.util.List;

import static ch.lambdaj.Lambda.extract;
import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.on;
import static org.hamcrest.Matchers.allOf;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.isIn;
import static org.hamcrest.Matchers.notNullValue;
import static ru.yandex.autotests.mordabackend.blocks.CleanvarsBlock.MAIL;
import static ru.yandex.autotests.mordabackend.useragents.UserAgent.FF_34;
import static ru.yandex.autotests.mordabackend.useragents.UserAgent.PDA;
import static ru.yandex.autotests.mordabackend.useragents.UserAgent.TOUCH;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.shouldHaveParameter;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.shouldHaveResponseCode;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.shouldMatchTo;
import static ru.yandex.autotests.mordabackend.utils.LinkUtils.addLink;
import static ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils.parameters;
import static ru.yandex.autotests.mordaexportsclient.MordaExports.MAIL_PROMO_BUTTON;
import static ru.yandex.autotests.mordaexportsclient.MordaExports.MAIL_PROMO_DISK_V12;
import static ru.yandex.autotests.mordaexportslib.ExportProvider.exports;
import static ru.yandex.autotests.mordaexportslib.matchers.DomainMatcher.domain;
import static ru.yandex.autotests.mordaexportslib.matchers.GeoMatcher.geo;
import static ru.yandex.autotests.mordaexportslib.matchers.LangMatcher.lang;
import static ru.yandex.autotests.utils.morda.url.Domain.BY;
import static ru.yandex.autotests.utils.morda.url.Domain.KZ;
import static ru.yandex.autotests.utils.morda.url.Domain.RU;
import static ru.yandex.autotests.utils.morda.url.Domain.UA;

/**
 * User: ivannik
 * Date: 28.07.2014
 */
@Aqua.Test(title = "Mail Promo Kubr")
@Features("Mail")
@Stories("Mail Promo Kubr")
@RunWith(CleanvarsParametrizedRunner.class)
public class PromoKubrMailTest {

    @CleanvarsParametrizedRunner.Parameters("{3}, {4}, {5}")
    public static ParametersUtils parameters =
            parameters(RU, UA, KZ, BY)
                    .withLanguages(Language.RU, Language.UK, Language.KK, Language.TT, Language.BE)
                    .withUserAgents(FF_34, PDA, TOUCH)
                    .withCleanvarsBlocks(MAIL);

    private final Client client;
    private final Cleanvars cleanvars;
    private final Region region;
    private final Language language;
    private final UserAgent userAgent;
    private final List<MailPromoButtonEntry> promoButton;
    private final List<MailPromoDiskV12Entry> promoDisk;

    public PromoKubrMailTest(MordaClient mordaClient, Client client, Cleanvars cleanvars, Region region,
                             Language language, UserAgent userAgent) {
        this.client = client;
        this.cleanvars = cleanvars;
        this.region = region;
        this.language = language;
        this.userAgent = userAgent;
        this.promoButton =
                exports(MAIL_PROMO_BUTTON,
                        domain(region.getDomain()),
                        lang(language), geo(region.getRegionIdInt()));
        this.promoDisk =
                exports(MAIL_PROMO_DISK_V12,
                        domain(region.getDomain()),
                        lang(language), geo(region.getRegionIdInt()));
    }

    @Test
    public void promoButton() throws IOException {
        shouldHaveParameter(cleanvars.getMail(), having(on(Mail.class).getPromoButton(), notNullValue()));
        shouldMatchTo(cleanvars.getMail().getPromoButton(), allOf(
            having(on(PromoButton.class).getColor(),
                    isIn(extract(promoButton, on(MailPromoButtonEntry.class).getColor()))),
            having(on(PromoButton.class).getCounter(),
                    isIn(extract(promoButton, on(MailPromoButtonEntry.class).getCounter()))),
            having(on(PromoButton.class).getDomain(),
                    isIn(extract(promoButton, on(MailPromoButtonEntry.class).getDomain()))),
            having(on(PromoButton.class).getGeo(),
                    isIn(extract(promoButton, on(MailPromoButtonEntry.class).getGeo()))),
            having(on(PromoButton.class).getLang(),
                    isIn(extract(promoButton, on(MailPromoButtonEntry.class).getLang()))),
            having(on(PromoButton.class).getText(),
                    isIn(extract(promoButton, on(MailPromoButtonEntry.class).getText()))),
            having(on(PromoButton.class).getUrl(),
                    isIn(extract(promoButton, on(MailPromoButtonEntry.class).getUrl())))
        ));
        addLink(cleanvars.getMail().getPromoButton().getUrl(), region, false, language, userAgent);
        shouldHaveResponseCode(client, cleanvars.getMail().getPromoButton().getUrl(), userAgent, equalTo(200));
    }

    @Test
    public void promoDiskV12() throws IOException {
        shouldHaveParameter(cleanvars.getMail(), having(on(Mail.class).getPromoDiskV12(), notNullValue()));
        shouldMatchTo(cleanvars.getMail().getPromoDiskV12(), allOf(
                having(on(PromoDisk.class).getCounter(),
                        isIn(extract(promoDisk, on(MailPromoDiskV12Entry.class).getCounter()))),
                having(on(PromoDisk.class).getDomain(),
                        isIn(extract(promoDisk, on(MailPromoDiskV12Entry.class).getDomain()))),
                having(on(PromoDisk.class).getGeo(),
                        isIn(extract(promoDisk, on(MailPromoDiskV12Entry.class).getGeo()))),
                having(on(PromoDisk.class).getGeoExclude(),
                        isIn(extract(promoDisk, on(MailPromoDiskV12Entry.class).getGeoExclude()))),
                having(on(PromoDisk.class).getLang(),
                        isIn(extract(promoDisk, on(MailPromoDiskV12Entry.class).getLang()))),
                having(on(PromoDisk.class).getText(),
                        isIn(extract(promoDisk, on(MailPromoDiskV12Entry.class).getText()))),
                having(on(PromoDisk.class).getUrl(),
                        isIn(extract(promoDisk, on(MailPromoDiskV12Entry.class).getUrl())))
        ));
        addLink(cleanvars.getMail().getPromoDiskV12().getUrl(), region, false, language, userAgent);
        shouldHaveResponseCode(client, cleanvars.getMail().getPromoDiskV12().getUrl(), userAgent, equalTo(200));
    }
}
