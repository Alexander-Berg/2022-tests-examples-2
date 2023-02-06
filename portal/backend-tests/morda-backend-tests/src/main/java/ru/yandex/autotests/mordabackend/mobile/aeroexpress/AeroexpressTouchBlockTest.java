package ru.yandex.autotests.mordabackend.mobile.aeroexpress;

import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mordabackend.MordaClient;
import ru.yandex.autotests.mordabackend.beans.aeroexpress.Aeroexpress;
import ru.yandex.autotests.mordabackend.beans.aeroexpress.AirportItem;
import ru.yandex.autotests.mordabackend.beans.aeroexpress.TrainItem;
import ru.yandex.autotests.mordabackend.beans.aeroexpress.TransportItem;
import ru.yandex.autotests.mordabackend.beans.cleanvars.Cleanvars;
import ru.yandex.autotests.mordabackend.useragents.UserAgent;
import ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils;
import ru.yandex.autotests.mordabackend.utils.runner.CleanvarsParametrizedRunner;
import ru.yandex.autotests.mordaexportsclient.beans.AeroexpressV2Entry;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import javax.ws.rs.client.Client;
import java.io.IOException;
import java.util.List;

import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.on;
import static ch.lambdaj.Lambda.select;
import static ch.lambdaj.Lambda.selectFirst;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.greaterThan;
import static org.hamcrest.Matchers.hasSize;
import static org.hamcrest.Matchers.isEmptyOrNullString;
import static org.hamcrest.Matchers.not;
import static ru.yandex.autotests.morda.utils.matchers.AllOfDetailedMatcher.allOfDetailed;
import static ru.yandex.autotests.morda.utils.matchers.NestedPropertyMatcher.hasPropertyWithValue;
import static ru.yandex.autotests.mordabackend.blocks.CleanvarsBlock.GEOID;
import static ru.yandex.autotests.mordabackend.blocks.CleanvarsBlock.LANGUAGE_LC;
import static ru.yandex.autotests.mordabackend.blocks.CleanvarsBlock.AEROEXPRESS;
import static ru.yandex.autotests.mordabackend.blocks.CleanvarsBlock.MORDA_ZONE;
import static ru.yandex.autotests.mordabackend.useragents.UserAgent.ANDROID_HTC_SENS;
import static ru.yandex.autotests.mordabackend.useragents.UserAgent.TOUCH;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.shouldHaveResponseCode;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.shouldMatchTo;
import static ru.yandex.autotests.mordabackend.utils.LinkUtils.normalizeUrl;
import static ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils.parameters;
import static ru.yandex.autotests.mordacommonsteps.matchers.RegexMatcher.matches;
import static ru.yandex.autotests.mordaexportsclient.MordaExports.AEROEXPRESS_V2;
import static ru.yandex.autotests.mordaexportslib.ExportProvider.exports;
import static ru.yandex.autotests.mordaexportslib.matchers.DomainMatcher.domain;
import static ru.yandex.autotests.mordaexportslib.matchers.GeoMatcher.geo;
import static ru.yandex.autotests.mordaexportslib.matchers.LangMatcher.lang;
import static ru.yandex.autotests.utils.morda.region.Region.MOSCOW;
import static ru.yandex.autotests.utils.morda.region.Region.SANKT_PETERBURG;

/**
 * @author Ivan Nikolaev <ivannik@yandex-team.ru>
 */
@Aqua.Test(title = "Aeroexpress Block")
@Features("Mobile")
@Stories("Aeroexpress Block")
@RunWith(CleanvarsParametrizedRunner.class)
public class AeroexpressTouchBlockTest {

    @CleanvarsParametrizedRunner.Parameters("{3}, {4}")
    public static ParametersUtils parameters =
            parameters(SANKT_PETERBURG, MOSCOW)
                    .withUserAgents(TOUCH, ANDROID_HTC_SENS)
                    .withCleanvarsBlocks(AEROEXPRESS, GEOID, MORDA_ZONE, LANGUAGE_LC);

    private final Cleanvars cleanvars;
    private final Client client;
    private final UserAgent userAgent;

    private List<AeroexpressV2Entry> aeroexpressV2Entries;

    public AeroexpressTouchBlockTest(MordaClient mordaClient, Client client, Cleanvars cleanvars, Region region,
                               UserAgent userAgent) {
        this.cleanvars = cleanvars;
        this.client = client;
        this.userAgent = userAgent;
    }

    @Before
    public void init() {
        aeroexpressV2Entries = exports(AEROEXPRESS_V2,
                domain(cleanvars.getMordaZone()), lang(cleanvars.getLanguageLc()), geo(cleanvars.getGeoID()));
        assertThat("Нет соответствующего экспорта aeroexpress_v2", aeroexpressV2Entries, hasSize(greaterThan(0)));
    }

    @Test
    public void aeroexpress() throws IOException {
        shouldMatchTo(cleanvars.getAeroexpress(), allOfDetailed(
                hasPropertyWithValue(on(Aeroexpress.class).getProcessed(), equalTo(1)),
                hasPropertyWithValue(on(Aeroexpress.class).getShow(), equalTo(1)),
                hasPropertyWithValue(on(Aeroexpress.class).getAirports(), hasSize(aeroexpressV2Entries.size()))
        ));
        for (AirportItem airportItem : cleanvars.getAeroexpress().getAirports()) {
            AeroexpressV2Entry export = selectFirst(aeroexpressV2Entries,
                    having(on(AeroexpressV2Entry.class).getId(), equalTo(airportItem.getId())));
            shouldMatchTo(airportItem, allOfDetailed(
                    hasPropertyWithValue(on(AirportItem.class).getId(), equalTo(airportItem.getId())),
                    hasPropertyWithValue(on(AirportItem.class).getLat(), equalTo(airportItem.getLat())),
                    hasPropertyWithValue(on(AirportItem.class).getLon(), equalTo(airportItem.getLon())),
                    hasPropertyWithValue(on(AirportItem.class).getRadius(), equalTo(airportItem.getRadius())),
                    hasPropertyWithValue(on(AirportItem.class).getTarget(), equalTo(airportItem.getTarget())),
                    hasPropertyWithValue(on(AirportItem.class).getTargetName(), equalTo(airportItem.getTargetName())),
                    hasPropertyWithValue(on(AirportItem.class).getTransports(),
                            hasSize(export.getTrainFrom() == null ? 1 : 2))
            ));

            checkTaxi(airportItem.getTransports(), export);
            if (export.getTrainFrom() != null) {
                checkAeroexpress(airportItem.getTransports(), export);
            }
        }
    }

    private void checkTaxi(List<TransportItem> transports, AeroexpressV2Entry export) {
        List<TransportItem> transportItems =
                select(transports, having(on(TransportItem.class).getType(), equalTo("taxi")));
        shouldMatchTo("Количество траниспорта типа taxi не равно 1", transportItems, hasSize(1));
        shouldMatchTo(transportItems.get(0), allOfDetailed(
                hasPropertyWithValue(on(TransportItem.class).getId(), equalTo(export.getId())),
                hasPropertyWithValue(on(TransportItem.class).getDuration(), matches("\\d+")),
                hasPropertyWithValue(on(TransportItem.class).getType(), equalTo("taxi")),
                hasPropertyWithValue(on(TransportItem.class).getTaxiCost(), equalTo(export.getTaxiCost())),
                hasPropertyWithValue(on(TransportItem.class).getOrderId(), isEmptyOrNullString()),
                hasPropertyWithValue(on(TransportItem.class).getTrains(), hasSize(0))
        ));
    }

    private void checkAeroexpress(List<TransportItem> transports, AeroexpressV2Entry export) throws IOException {
        List<TransportItem> transportItems =
                select(transports, having(on(TransportItem.class).getType(), equalTo("aeroexpress")));
        shouldMatchTo("Количество траниспорта типа aeroexpress не равно 1",  transportItems, hasSize(1));
        shouldMatchTo(transportItems.get(0), allOfDetailed(
                hasPropertyWithValue(on(TransportItem.class).getId(), equalTo(export.getId())),
                hasPropertyWithValue(on(TransportItem.class).getDuration(), matches("\\d+")),
                hasPropertyWithValue(on(TransportItem.class).getType(), equalTo("aeroexpress")),
                hasPropertyWithValue(on(TransportItem.class).getTaxiCost(), isEmptyOrNullString()),
                hasPropertyWithValue(on(TransportItem.class).getOrderId(), equalTo(export.getOrderId())),
                hasPropertyWithValue(on(TransportItem.class).getTrains(), hasSize(greaterThan(0)))
        ));

        for (TrainItem trainItems : transportItems.get(0).getTrains()) {
            shouldMatchTo(trainItems, allOfDetailed(
                    hasPropertyWithValue(on(TrainItem.class).getDuration(), matches("\\d+")),
                    hasPropertyWithValue(on(TrainItem.class).getDeparture(), not(isEmptyOrNullString())),
                    hasPropertyWithValue(on(TrainItem.class).getUrl(),
                            matches("https://rasp\\.yandex\\.ru/thread/[\\d\\w_]+"))
            ));
            shouldHaveResponseCode(client, normalizeUrl(trainItems.getUrl()), userAgent, equalTo(200));
        }
    }
}
