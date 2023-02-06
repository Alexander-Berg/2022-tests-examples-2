package ru.yandex.autotests.mordabackend.search;

import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mordabackend.MordaClient;
import ru.yandex.autotests.mordabackend.Properties;
import ru.yandex.autotests.mordabackend.beans.cleanvars.Cleanvars;
import ru.yandex.autotests.mordabackend.beans.search.Promo;
import ru.yandex.autotests.mordabackend.beans.search.Search;
import ru.yandex.autotests.mordabackend.useragents.UserAgent;
import ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils;
import ru.yandex.autotests.mordabackend.utils.runner.CleanvarsParametrizedRunner;
import ru.yandex.autotests.mordaexportsclient.MordaExports;
import ru.yandex.autotests.mordaexportsclient.beans.SearchPromolinkEntry;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import javax.ws.rs.client.Client;
import java.io.IOException;
import java.util.Collections;
import java.util.List;

import static ch.lambdaj.Lambda.extract;
import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.on;
import static org.hamcrest.Matchers.*;
import static org.junit.Assume.assumeThat;
import static ru.yandex.autotests.mordabackend.blocks.CleanvarsBlock.SEARCH;
import static ru.yandex.autotests.mordabackend.blocks.CleanvarsBlock.SEARCHURL;
import static ru.yandex.autotests.mordabackend.blocks.CleanvarsBlock.YYYYMMDD;
import static ru.yandex.autotests.mordabackend.search.SearchUtils.*;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.*;
import static ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils.parameters;
import static ru.yandex.autotests.mordabackend.utils.predicates.ExportDateMatcher.after;
import static ru.yandex.autotests.mordabackend.utils.predicates.ExportDateMatcher.before;
import static ru.yandex.autotests.mordaexportslib.ExportProvider.exports;
import static ru.yandex.autotests.mordaexportslib.matchers.DomainMatcher.domain;
import static ru.yandex.autotests.mordaexportslib.matchers.GeoMatcher.geo;
import static ru.yandex.autotests.mordaexportslib.matchers.LangMatcher.lang;

/**
 * User: ivannik
 * Date: 25.07.2014
 */
@Aqua.Test(title = "Search Block")
@Features("Search")
@Stories("Search Block")
@RunWith(CleanvarsParametrizedRunner.class)
public class SearchBlockTest {

    private static final Properties CONFIG = new Properties();

    @CleanvarsParametrizedRunner.Parameters("{3}, {4}, {5}")
    public static ParametersUtils parameters =
            parameters(SEARCH_REGIONS_ALL)
                    .withLanguages(LANGUAGES)
                    .withUserAgents(USER_AGENTS)
                    .withCleanvarsBlocks(YYYYMMDD, SEARCH, SEARCHURL);

    private Client client;
    private Region region;
    private Language language;
    private UserAgent userAgent;
    private Cleanvars cleanvars;
    private List<SearchPromolinkEntry> searchPromolinkEntry;

    public SearchBlockTest(MordaClient mordaClient, Client client, Cleanvars cleanvars,
                           Region region, Language language, UserAgent userAgent) {
        this.client = client;
        this.region = region;
        this.language = language;
        this.cleanvars = cleanvars;
        this.userAgent = userAgent;
    }

    @Before
    public void setUp() {
        MordaExports.MordaExport<SearchPromolinkEntry> exp = USER_AGENT_EXPORTS.get(userAgent);
        if (exp != null) {
            this.searchPromolinkEntry = exports(exp,
                    having(on(SearchPromolinkEntry.class).getFrom(), before(cleanvars.getYYYYMMDD())),
                    having(on(SearchPromolinkEntry.class).getTill(), after(cleanvars.getYYYYMMDD())),
                    domain(region.getDomain()), lang(language), geo(region.getRegionIdInt()));
        } else {
            this.searchPromolinkEntry = Collections.emptyList();
        }
    }

    @Test
    public void searchUrl() throws IOException {
        shouldMatchTo(cleanvars.getSearchUrl(),
                equalTo(getSearchLink(userAgent, region.getDomain())));
        shouldHaveParameter(cleanvars.getSearch(), having(on(Search.class).getUrl(),
                equalTo(getSearchLink(userAgent, region.getDomain()))));
        shouldHaveResponseCode(client,
                cleanvars.getSearchUrl() + getSearchRequest(SEARCH_REQUEST), userAgent, equalTo(200));
    }

    @Test
    public void promoExists() {
        if (searchPromolinkEntry.isEmpty()) {
            shouldHaveParameter(cleanvars.getSearch(), having(on(Search.class).getPromo(), nullValue()));
        } else {
            shouldHaveParameter(cleanvars.getSearch(), having(on(Search.class).getPromo(), not(empty())));
        }
    }

    @Test
    public void promoContent() throws IOException {
        assumeThat(searchPromolinkEntry, not(empty()));
        shouldHaveParameter(cleanvars.getSearch(), having(on(Search.class).getPromo(), notNullValue()));
        shouldMatchTo(cleanvars.getSearch().getPromo(), allOf(
                having(on(Promo.class).getBk(),
                        isIn(extract(searchPromolinkEntry, on(SearchPromolinkEntry.class).getBk()))),
                having(on(Promo.class).getCounter(),
                        isIn(extract(searchPromolinkEntry, on(SearchPromolinkEntry.class).getCounter()))),
                having(on(Promo.class).getDomain(),
                        isIn(extract(searchPromolinkEntry, on(SearchPromolinkEntry.class).getDomain()))),
                having(on(Promo.class).getFrom(),
                        isIn(extract(searchPromolinkEntry, on(SearchPromolinkEntry.class).getFrom()))),
                having(on(Promo.class).getGeo(),
                        isIn(extract(searchPromolinkEntry, on(SearchPromolinkEntry.class).getGeo()))),
                having(on(Promo.class).getLang(),
                        isIn(extract(searchPromolinkEntry, on(SearchPromolinkEntry.class).getLang()))),
                having(on(Promo.class).getText(),
                        isIn(extract(searchPromolinkEntry, on(SearchPromolinkEntry.class).getText()))),
                having(on(Promo.class).getUrl(),
                        isIn(extract(searchPromolinkEntry, on(SearchPromolinkEntry.class).getUrl())))
        ));
    }

    @Test
    public void processedFlag() {
        shouldHaveParameter(cleanvars.getSearch(), having(on(Search.class).getProcessed(), equalTo(1)));
    }
}
