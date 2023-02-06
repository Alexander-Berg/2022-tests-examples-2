package ru.yandex.metrika.expenses.connectors.google;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.time.LocalDate;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;
import java.util.Set;

import com.google.ads.googleads.v9.services.GoogleAdsRow;
import com.google.protobuf.TextFormat;
import org.apache.commons.compress.utils.Lists;
import org.junit.Assert;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;

import ru.yandex.metrika.api.management.client.connectors.AdsCabinetEnriched;
import ru.yandex.metrika.api.management.client.connectors.AdsPlatform;
import ru.yandex.metrika.api.management.client.connectors.google.GoogleApiClient;
import ru.yandex.metrika.util.log.Log4jSetup;

import static org.junit.Assert.assertEquals;
import static org.mockito.Matchers.any;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

public class GoogleConnectorSkAdReportLoaderTest {
    private GoogleApiClient googleApiClientMock;
    private AdsCabinetEnriched cabinet;
    private GoogleConnectorSkAdReportLoader reportLoader;

    @BeforeClass
    public static void initClass() {
        Log4jSetup.basicSetup();
    }

    private static AdsCabinetEnriched buildCabinet() {
        Set<String> domains = Set.of(
                "metrika.yandex.ru",
                "metrika.yandex.ua",
                "metrica.yandex.com",
                "metrica.yandex.com.tr",
                "webvisor.com",
                "metrika.yandex.by",
                "metrika.yandex.kz"
        );

        AdsCabinetEnriched cabinet = new AdsCabinetEnriched();
        cabinet.setConnectorId(1);
        cabinet.setCounterId(1);
        cabinet.setPlatform(AdsPlatform.GOOGLE);
        cabinet.setCustomerAccountId(1L);
        cabinet.setCustomerAccountName("CustomerAccountName");
        cabinet.setCustomerAccountTimezone("Europe/Moscow");
        cabinet.setCustomerAccountCurrency("RUB");
        cabinet.setManagedBy(1L);
        cabinet.setDomainFilter(domains::contains);
        cabinet.setStartDate(LocalDate.now().minusDays(7));
        cabinet.setEndDate(LocalDate.now());
        return cabinet;
    }

    @Before
    public void init() {
        googleApiClientMock = mock(GoogleApiClient.class);
        cabinet = buildCabinet();
        reportLoader = new GoogleConnectorSkAdReportLoader(googleApiClientMock);
    }

    @Test
    public void testLoadExpensesReportFromApi() {
        when(googleApiClientMock.fetchGoogleSkAdReport(any(AdsCabinetEnriched.class)))
                .thenReturn(loadGoogleAdsRows("skad_valid_rows").iterator());

        Iterator<GoogleSkAdRow> it = reportLoader.loadExpensesReportFromApi(cabinet);
        List<GoogleSkAdRow> result = Lists.newArrayList(it);

        Assert.assertEquals(7, result.size());
        assertEquals(7, cabinet.getStat().getTotalRowsCount());
        assertEquals(7, cabinet.getStat().getReportRowsCount());

        assertEquals(19, result.stream().map(GoogleSkAdRow::getSkAdNetworkConversions).reduce(Long::sum).orElseThrow().intValue());
        assertEquals(103, result.stream().map(GoogleSkAdRow::getSkAdNetworkConversionValue).reduce(Long::sum).orElseThrow().intValue());
    }

    private List<GoogleAdsRow> loadGoogleAdsRows(String fileName) {
        List<GoogleAdsRow> result = new ArrayList<>();

        try (
                BufferedReader reader =
                        new BufferedReader(new InputStreamReader(this.getClass().getResourceAsStream("test_data/" + fileName)))
        ) {
            String line;
            while ((line = reader.readLine()) != null) {
                GoogleAdsRow.Builder builder = GoogleAdsRow.newBuilder();
                TextFormat.merge(line, builder);
                result.add(builder.build());
            }
        } catch (Exception e) {
            throw new RuntimeException(e);
        }

        return result;
    }
}
