package ru.yandex.autotests.mordabackend.geo;

import org.junit.Test;
import org.junit.runner.RunWith;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mordabackend.MordaClient;
import ru.yandex.autotests.mordabackend.Properties;
import ru.yandex.autotests.mordabackend.beans.cleanvars.Cleanvars;
import ru.yandex.autotests.mordabackend.beans.geo.Geo;
import ru.yandex.autotests.mordabackend.beans.geo.Maps;
import ru.yandex.autotests.mordabackend.useragents.UserAgent;
import ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils;
import ru.yandex.autotests.mordabackend.utils.runner.CleanvarsParametrizedRunner;
import ru.yandex.autotests.mordaexportsclient.beans.MapsEntry;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import javax.ws.rs.client.Client;
import java.io.IOException;
import java.text.ParseException;

import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.on;
import static org.hamcrest.Matchers.allOf;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.notNullValue;
import static org.hamcrest.Matchers.nullValue;
import static ru.yandex.autotests.mordabackend.blocks.CleanvarsBlock.GEO;
import static ru.yandex.autotests.mordabackend.geo.GeoUtils.CLENVARS_DATE_FORMAT;
import static ru.yandex.autotests.mordabackend.geo.GeoUtils.EXP_DATE_FORMAT;
import static ru.yandex.autotests.mordabackend.geo.GeoUtils.GEO_REGIONS_ALL;
import static ru.yandex.autotests.mordabackend.geo.GeoUtils.LANGUAGES;
import static ru.yandex.autotests.mordabackend.useragents.UserAgent.FF_34;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.shouldHaveParameter;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.shouldHaveResponseCode;
import static ru.yandex.autotests.mordabackend.utils.LinkUtils.normalizeUrl;
import static ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils.parameters;
import static ru.yandex.autotests.mordacommonsteps.matchers.LanguageMatcher.inLanguage;
import static ru.yandex.autotests.mordaexportsclient.MordaExports.MAPS;
import static ru.yandex.autotests.mordaexportslib.ExportProvider.export;
import static ru.yandex.autotests.mordaexportslib.matchers.GeoMatcher.geo;
import static ru.yandex.autotests.mordaexportslib.matchers.LangMatcher.lang;
import static ru.yandex.autotests.mordaexportslib.matchers.MordatypeMatcher.mordatype;

/**
 * User: ivannik
 * Date: 14.07.2014
 */
@Aqua.Test(title = "Geo Block Commons")
@Features("Geo")
@Stories("Geo Block Commons")
@RunWith(CleanvarsParametrizedRunner.class)
public class GeoBlockTest {
    private static final Properties CONFIG = new Properties();

    @CleanvarsParametrizedRunner.Parameters("{3}, {4}, {5}")
    public static ParametersUtils parameters =
            parameters(GEO_REGIONS_ALL)
                    .withLanguages(LANGUAGES)
                    .withUserAgents(FF_34)
                    .withCleanvarsBlocks(GEO);

    private Language language;
    private Client client;
    private Cleanvars cleanvars;
    private UserAgent userAgent;
    private MapsEntry mapsEntry;
    private MapsEntry notNullUrlmapsEntry;


    public GeoBlockTest(MordaClient mordaClient, Client client, Cleanvars cleanvars,
                        Region region, Language language, UserAgent userAgent) {
        this.language = language;
        this.client = client;
        this.cleanvars = cleanvars;
        this.userAgent = userAgent;
        this.mapsEntry = export(MAPS, geo(region.getRegionIdInt()),
                mordatype(region.getDomain().getValue().replace(".", "")), lang(language));
        this.notNullUrlmapsEntry = export(MAPS, geo(region.getRegionIdInt()), having(on(MapsEntry.class).getUrl(),
                        notNullValue()),  mordatype(region.getDomain().getValue().replace(".", "")), lang(language));

    }

    @Test
    public void mapsLink() throws IOException {
        if (notNullUrlmapsEntry != null) {
            shouldHaveParameter(cleanvars.getGeo().getMaps().getObj(), allOf(
                    having(on(Maps.class).getRawMapsurl(), equalTo(notNullUrlmapsEntry.getUrl())),
                    having(on(Maps.class).getMapsurl(), equalTo(notNullUrlmapsEntry.getUrl().replace("&", "&amp;"))),
                    having(on(Maps.class).getUrl(), equalTo(notNullUrlmapsEntry.getUrl()))));
            shouldHaveResponseCode(client,
                    normalizeUrl(cleanvars.getGeo().getMaps().getObj().getRawMapsurl()), userAgent, equalTo(200));
        } else {
            shouldHaveParameter(cleanvars.getGeo().getMaps().getObj(), allOf(
                    having(on(Maps.class).getRawMapsurl(), nullValue()),
                    having(on(Maps.class).getMapsurl(), nullValue()),
                    having(on(Maps.class).getUrl(), nullValue())));
        }
    }

    @Test
    public void mapsNarodLink() throws IOException {
        shouldHaveParameter(cleanvars.getGeo().getMaps().getObj(), having(on(Maps.class).getNarod(),
                equalTo(mapsEntry.getNarod())));
        if (mapsEntry.getNarod() != null) {
            shouldHaveResponseCode(client, cleanvars.getGeo().getMaps().getObj().getNarod(), userAgent, equalTo(200));
        }
    }

    @Test
    public void mapsText() {
        if (mapsEntry.getText() != null) {
            shouldHaveParameter(cleanvars.getGeo().getMaps().getObj(), having(on(Maps.class).getName(),
                    equalTo(mapsEntry.getText())));
        } else {
            shouldHaveParameter(cleanvars.getGeo().getMaps().getObj(), having(on(Maps.class).getName(),
                    inLanguage(language)));
        }
    }

    @Test
    public void mapsGeo() {
        shouldHaveParameter(cleanvars.getGeo().getMaps().getObj(), having(on(Maps.class).getGeo(),
                equalTo(mapsEntry.getGeo())));
    }

    @Test
    public void mapsLang() {
        shouldHaveParameter(cleanvars.getGeo().getMaps().getObj(), having(on(Maps.class).getLang(),
                equalTo(mapsEntry.getLang())));
    }

    @Test
    public void mapsNewfrom() {
        shouldHaveParameter(cleanvars.getGeo().getMaps().getObj(), having(on(Maps.class).getNewfrom(),
                equalTo(mapsEntry.getNewfrom())));
    }

    @Test
    public void mapsNewto() {
        shouldHaveParameter(cleanvars.getGeo().getMaps().getObj(), having(on(Maps.class).getNewto(),
                equalTo(mapsEntry.getNewto())));
    }

    @Test
    public void mapsUpdatedfrom() throws ParseException {
        shouldHaveParameter(cleanvars.getGeo().getMaps().getObj(), having(on(Maps.class).getUpdatedfrom(),
                equalTo(mapsEntry.getUpdatedfrom())));
        if (mapsEntry.getUpdatedfrom() != null) {
            shouldHaveParameter(cleanvars.getGeo().getMaps().getObj(), having(on(Maps.class).getMapsUpdatedDate(),
                    equalTo(CLENVARS_DATE_FORMAT.print(EXP_DATE_FORMAT.parseLocalDate(mapsEntry.getUpdatedfrom())))));
        }
    }

    @Test
    public void mapsUpdatedto() {
        shouldHaveParameter(cleanvars.getGeo().getMaps().getObj(), having(on(Maps.class).getUpdatedto(),
                equalTo(mapsEntry.getUpdatedto())));
    }

    @Test
    public void mapsMordatype() {
        shouldHaveParameter(cleanvars.getGeo().getMaps().getObj(), having(on(Maps.class).getMordatype(),
                equalTo(mapsEntry.getMordatype())));
    }

    @Test
    public void showFlag() {
        shouldHaveParameter(cleanvars.getGeo(), having(on(Geo.class).getShow(), equalTo(1)));
    }

    @Test
    public void processedFlag() {
        shouldHaveParameter(cleanvars.getGeo(), having(on(Geo.class).getProcessed(), equalTo(1)));
    }
}
