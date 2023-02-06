package ru.yandex.autotests.mordabackend.afisha;

import org.hamcrest.Matcher;
import org.junit.Test;
import org.junit.runner.RunWith;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mordabackend.MordaClient;
import ru.yandex.autotests.mordabackend.beans.afisha.Afisha;
import ru.yandex.autotests.mordabackend.beans.afisha.AfishaPromo;
import ru.yandex.autotests.mordabackend.beans.cleanvars.Cleanvars;
import ru.yandex.autotests.mordabackend.useragents.UserAgent;
import ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils;
import ru.yandex.autotests.mordabackend.utils.runner.CleanvarsParametrizedRunner;
import ru.yandex.autotests.mordaexportsclient.beans.AfishaPromoV2Entry;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import javax.ws.rs.client.Client;
import java.io.IOException;
import java.util.List;

import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.on;
import static org.hamcrest.Matchers.empty;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.greaterThanOrEqualTo;
import static org.hamcrest.Matchers.hasItem;
import static org.hamcrest.Matchers.not;
import static org.hamcrest.Matchers.startsWith;
import static org.junit.Assert.assertThat;
import static org.junit.Assume.assumeThat;
import static org.junit.Assume.assumeTrue;
import static ru.yandex.autotests.morda.utils.matchers.AllOfDetailedMatcher.allOfDetailed;
import static ru.yandex.autotests.mordabackend.afisha.AfishaUtils.AFISHA_REGIONS_ALL;
import static ru.yandex.autotests.mordabackend.afisha.AfishaUtils.LANGUAGES;
import static ru.yandex.autotests.mordabackend.afisha.AfishaUtils.getAfishaHref;
import static ru.yandex.autotests.mordabackend.afisha.AfishaUtils.getExpectedNumberOfAfishaEvents;
import static ru.yandex.autotests.mordabackend.blocks.CleanvarsBlock.AFISHA;
import static ru.yandex.autotests.mordabackend.blocks.CleanvarsBlock.YYYYMMDD;
import static ru.yandex.autotests.mordabackend.useragents.UserAgent.FF_34;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.shouldHaveParameter;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.shouldHaveResponseCode;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.shouldMatchTo;
import static ru.yandex.autotests.mordabackend.utils.LinkUtils.addLink;
import static ru.yandex.autotests.mordabackend.utils.LinkUtils.normalizeUrl;
import static ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils.parameters;
import static ru.yandex.autotests.mordabackend.utils.predicates.ExportDateMatcher.after;
import static ru.yandex.autotests.mordabackend.utils.predicates.ExportDateMatcher.before;
import static ru.yandex.autotests.mordaexportsclient.MordaExports.AFISHA_PROMO_V2;
import static ru.yandex.autotests.mordaexportslib.ExportProvider.exports;
import static ru.yandex.autotests.mordaexportslib.matchers.DomainMatcher.domain;
import static ru.yandex.autotests.mordaexportslib.matchers.GeoMatcher.geo;
import static ru.yandex.autotests.mordaexportslib.matchers.LangMatcher.lang;

/**
 * User: ivannik
 * Date: 30.06.2014
 */
@Aqua.Test(title = "Afisha Block")
@Features("Afisha")
@Stories("Afisha Block")
@RunWith(CleanvarsParametrizedRunner.class)
public class AfishaTest {

    @CleanvarsParametrizedRunner.Parameters("{3}, {4}, {5}")
    public static ParametersUtils parameters =
            parameters(AFISHA_REGIONS_ALL)
                    .withLanguages(LANGUAGES)
                    .withUserAgents(FF_34)
                    .withCleanvarsBlocks(AFISHA, YYYYMMDD);

    private final MordaClient mordaClient;
    private final Client client;
    private Region region;
    private Language language;
    private UserAgent userAgent;
    private Cleanvars cleanvars;
    private String afishaHref;
    private List<AfishaPromoV2Entry> afishaPromoEntries;

    public AfishaTest(MordaClient mordaClient, Client client, Cleanvars cleanvars,
                      Region region, Language language, UserAgent userAgent) {
        this.region = region;
        this.userAgent = userAgent;
        this.client = client;
        this.mordaClient = mordaClient;
        this.cleanvars = cleanvars;
        this.afishaHref = getAfishaHref(userAgent, region);
        this.afishaPromoEntries = exports(AFISHA_PROMO_V2, domain(region.getDomain()), lang(language),
                geo(region.getRegionIdInt()),
                having(on(AfishaPromoV2Entry.class).getContent(), equalTo("big")),
                having(on(AfishaPromoV2Entry.class).getFrom(), before(cleanvars.getYYYYMMDD())),
                having(on(AfishaPromoV2Entry.class).getTill(), after(cleanvars.getYYYYMMDD())));
    }

    @Test
    public void afishaLink() throws IOException {
        shouldHaveParameter(normalizeUrl(cleanvars.getAfisha().getHref()), startsWith(afishaHref));
        addLink(cleanvars.getAfisha().getHref(), region, false, language, userAgent);
        shouldHaveResponseCode(client, normalizeUrl(cleanvars.getAfisha().getHref()), userAgent, equalTo(200));
    }

    @Test
    public void eventsCount() {
        assumeTrue(region.equals(Region.MOSCOW) || region.equals(Region.SPB) || region.equals(Region.KIEV));
        int premiers = cleanvars.getAfisha().getPremiere() == null ? 0 : 1;
        int eventsCount = cleanvars.getAfisha().getEvents().size() + premiers +
                (cleanvars.getAfisha().getPromo() == null ? 0 : 1);
        assertThat("Неверное число событий: ", eventsCount,
                greaterThanOrEqualTo(getExpectedNumberOfAfishaEvents(region)));
    }

    @Test
    public void afishaPromo() throws IOException {
        assumeThat("No afisha promo export", afishaPromoEntries, not(empty()));
        AfishaPromo promo = cleanvars.getAfisha().getPromo();
        Matcher<AfishaPromoV2Entry> entryMatcher = allOfDetailed(
                having(on(AfishaPromoV2Entry.class).getDomain(), equalTo(promo.getDomain())),
                having(on(AfishaPromoV2Entry.class).getContent(), equalTo(promo.getContent())),
                having(on(AfishaPromoV2Entry.class).getLang(), equalTo(promo.getLang())),
                having(on(AfishaPromoV2Entry.class).getFrom(), equalTo(promo.getFrom())),
                having(on(AfishaPromoV2Entry.class).getTill(), equalTo(promo.getTill())),
                having(on(AfishaPromoV2Entry.class).getDate(), equalTo(promo.getDate())),
                having(on(AfishaPromoV2Entry.class).getTextDate(), equalTo(promo.getTextDate())),
                having(on(AfishaPromoV2Entry.class).getUrlHttps(), equalTo(promo.getUrlHttps())),
                having(on(AfishaPromoV2Entry.class).getIcon(), equalTo(promo.getIcon())),
                having(on(AfishaPromoV2Entry.class).getCounter(), equalTo(promo.getCounter())),
                having(on(AfishaPromoV2Entry.class).getType(), equalTo(promo.getType()))
        );
        shouldMatchTo(afishaPromoEntries, hasItem(entryMatcher));
        shouldHaveResponseCode(client, cleanvars.getAfisha().getPromo().getUrlHttps(), userAgent, equalTo(200));
        if (cleanvars.getAfisha().getPromo().getIcon() != null) {
            shouldHaveResponseCode(client, cleanvars.getAfisha().getPromo().getIcon(), userAgent, equalTo(200));
        }
    }

    @Test
    public void showFlag() {
        int premiers = cleanvars.getAfisha().getPremiere() == null ? 0 : 1;
        int eventsCount = cleanvars.getAfisha().getEvents().size() + premiers;
        if (eventsCount > 0) {
            shouldHaveParameter(cleanvars.getAfisha(), having(on(Afisha.class).getShow(), equalTo(1)));
        } else {
            shouldHaveParameter(cleanvars.getAfisha(), having(on(Afisha.class).getShow(), equalTo(0)));
        }
    }

    @Test
    public void processedFlag() {
        shouldHaveParameter(cleanvars.getAfisha(), having(on(Afisha.class).getProcessed(), equalTo(1)));
    }
}
