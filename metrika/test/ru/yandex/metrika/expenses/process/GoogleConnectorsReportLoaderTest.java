package ru.yandex.metrika.expenses.process;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Iterator;
import java.util.List;
import java.util.Optional;
import java.util.Set;
import java.util.stream.Collectors;

import com.google.ads.googleads.v9.services.GoogleAdsRow;
import com.google.protobuf.TextFormat;
import org.apache.commons.compress.utils.Lists;
import org.apache.commons.lang3.StringUtils;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;

import ru.yandex.metrika.api.management.client.connectors.AdsCabinetEnriched;
import ru.yandex.metrika.api.management.client.connectors.AdsPlatform;
import ru.yandex.metrika.api.management.client.connectors.google.GoogleApiClient;
import ru.yandex.metrika.api.management.client.uploading.ExpenseUploadingRow;
import ru.yandex.metrika.expenses.connectors.google.GoogleConnectorsReportLoader;
import ru.yandex.metrika.expenses.connectors.google.GoogleConnectorsStateStorageYdb;
import ru.yandex.metrika.expenses.connectors.google.GoogleExpensesRow;
import ru.yandex.metrika.expenses.connectors.google.GoogleExpensesYdbRow;
import ru.yandex.metrika.managers.Currency;
import ru.yandex.metrika.managers.CurrencyService;
import ru.yandex.metrika.util.log.Log4jSetup;

import static org.junit.Assert.assertEquals;
import static org.mockito.Matchers.any;
import static org.mockito.Matchers.anyBoolean;
import static org.mockito.Matchers.anyLong;
import static org.mockito.Matchers.anyString;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

public class GoogleConnectorsReportLoaderTest {

    private GoogleApiClient googleApiClientMock;
    private GoogleConnectorsStateStorageYdb connectorsExpensesStorageMock;
    private CurrencyService currencyServiceMock;
    private AdsCabinetEnriched cabinet;
    private Currency currency;
    private GoogleConnectorsReportLoader reportLoader;

    @BeforeClass
    public static void initClass() {
        Log4jSetup.basicSetup();
    }

    @Before
    public void init() throws Exception {
        googleApiClientMock = mock(GoogleApiClient.class);
        connectorsExpensesStorageMock = mock(GoogleConnectorsStateStorageYdb.class);
        currencyServiceMock = mock(CurrencyService.class);
        cabinet = buildCabinet();
        currency = new Currency(643, "RUB", "Российский рубль");
        reportLoader = new GoogleConnectorsReportLoader(
                googleApiClientMock,
                connectorsExpensesStorageMock,
                currencyServiceMock
        );
        when(currencyServiceMock.getCurrency(anyString())).thenReturn(Optional.of(currency));
    }

    @Test
    public void testEmptyApiResponse() {
        when(googleApiClientMock.fetchGoogleAdsReport(any(AdsCabinetEnriched.class)))
                .thenReturn(loadGoogleAdsRows("empty").iterator());
        when(googleApiClientMock.fetchGoogleAdsConversionReport(any(AdsCabinetEnriched.class)))
                .thenReturn(loadGoogleAdsRows("empty").iterator());

        Iterator<GoogleExpensesRow> it = reportLoader.loadExpensesReportFromApi(cabinet);
        List<GoogleExpensesRow> result = Lists.newArrayList(it);

        assertEquals(0, result.size());
        assertEquals(0, cabinet.getStat().getTotalRowsCount());
        assertEquals(0, cabinet.getStat().getReportRowsCount());
        assertEquals(0, cabinet.getStat().getUtmSourceCount());
        assertEquals(0, cabinet.getStat().getCompatibleDomainCount());
    }

    @Test
    public void testApiResponseWithData() {
        when(googleApiClientMock.fetchGoogleAdsReport(any(AdsCabinetEnriched.class)))
                .thenReturn(loadGoogleAdsRows("all_valid_rows").iterator());
        when(googleApiClientMock.fetchGoogleAdsConversionReport(any(AdsCabinetEnriched.class)))
                .thenReturn(loadGoogleAdsRows("empty").iterator());

        Iterator<GoogleExpensesRow> it = reportLoader.loadExpensesReportFromApi(cabinet);
        List<GoogleExpensesRow> result = Lists.newArrayList(it);

        assertEquals(20, result.size());
        assertEquals(20, cabinet.getStat().getTotalRowsCount());

        assertEquals(677L, result.stream().map(GoogleExpensesRow::getImpressions).reduce(Long::sum).orElseThrow().longValue());
        assertEquals(102L, result.stream().map(GoogleExpensesRow::getClicks).reduce(Long::sum).orElseThrow().longValue());
        assertEquals(2228310000L, result.stream().map(GoogleExpensesRow::getCostMicros).reduce(Long::sum).orElseThrow().longValue());

        assertEquals(19, result.stream().filter(r -> StringUtils.isNotEmpty(r.getCampaignTrackingUrlTemplate())).count());
        assertEquals(1, result.stream().filter(r -> StringUtils.isNotEmpty(r.getCampaignFinalUrlSuffix())).count());
        assertEquals(20, result.stream().filter(r -> r.getAdGroupAdAdFinalUrls() != null && !r.getAdGroupAdAdFinalUrls().isEmpty()).count());
    }

    @Test
    public void testApiResponseWithData2() {
        when(googleApiClientMock.fetchGoogleAdsReport(any(AdsCabinetEnriched.class)))
                .thenReturn(loadGoogleAdsRows("all_valid_rows2").iterator());
        when(googleApiClientMock.fetchGoogleAdsConversionReport(any(AdsCabinetEnriched.class)))
                .thenReturn(loadGoogleAdsRows("empty").iterator());

        Iterator<GoogleExpensesRow> it = reportLoader.loadExpensesReportFromApi(cabinet);
        List<GoogleExpensesRow> result = Lists.newArrayList(it);

        assertEquals(1163, result.size());
        assertEquals(1163, cabinet.getStat().getTotalRowsCount());

        assertEquals(4146L, result.stream().map(GoogleExpensesRow::getImpressions).reduce(Long::sum).orElseThrow().longValue());
        assertEquals(239L, result.stream().map(GoogleExpensesRow::getClicks).reduce(Long::sum).orElseThrow().longValue());
        assertEquals(2771310000L, result.stream().map(GoogleExpensesRow::getCostMicros).reduce(Long::sum).orElseThrow().longValue());

        assertEquals(1163, result.stream().filter(r -> StringUtils.isNotEmpty(r.getAdGroupTrackingUrlTemplate())).count());
        assertEquals(1163, result.stream().filter(r -> r.getAdGroupAdAdFinalUrls() != null && !r.getAdGroupAdAdFinalUrls().isEmpty()).count());
    }

    @Test
    public void testStatGathering() {
        when(connectorsExpensesStorageMock.load(anyLong(), any(LocalDate.class), anyBoolean()))
                .thenReturn(loadGoogleExpensesYdbRows("all_valid_rows.tskv").iterator());

        Iterator<ExpenseUploadingRow> it = reportLoader.loadExpensesFromYdb(cabinet);
        List<ExpenseUploadingRow> result = Lists.newArrayList(it);

        assertEquals(20, result.size());
        assertEquals(20, cabinet.getStat().getTotalRowsCount());
        assertEquals(20, cabinet.getStat().getReportRowsCount());
        assertEquals(20, cabinet.getStat().getUtmSourceCount());
        assertEquals(20, cabinet.getStat().getCompatibleDomainCount());
    }

    @Test
    public void testParamsSubstitution() {
        when(connectorsExpensesStorageMock.load(anyLong(), any(LocalDate.class), anyBoolean()))
                .thenReturn(loadGoogleExpensesYdbRows("all_valid_rows.tskv").iterator());

        Iterator<ExpenseUploadingRow> it = reportLoader.loadExpensesFromYdb(cabinet);
        List<ExpenseUploadingRow> result = Lists.newArrayList(it);

        assertEquals(Collections.nCopies(20, "google"),
                result.stream().map(ExpenseUploadingRow::utmSource).collect(Collectors.toList()));
        assertEquals(Collections.nCopies(20, "search"),
                result.stream().map(ExpenseUploadingRow::utmMedium).collect(Collectors.toList()));
        assertEquals(
                List.of(
                        "900819053", "900819053", "8146429199", "8146429199", "9522886753", "900819053", "900819053",
                        "900819053", "900819053", "900819053", "900819053", "755479567", "759907177", "759907177", "759907177",
                        "755479567", "755479567", "755479567", "755479567", "755479567"
                ), result.stream().map(ExpenseUploadingRow::utmCampaign).collect(Collectors.toList()));
        assertEquals(
                List.of(
                        "400261199215", "211560037134", "397582312057", "397565145777", "421575430471", "211560036888",
                        "211560036894", "211560036921", "211560037089", "211560036924", "211560036927", "184441445518",
                        "181329323643", "181329323661", "197948574670", "178394009434", "191040815458", "178271565337",
                        "324531666610", "189690552887"
                ), result.stream().map(ExpenseUploadingRow::utmContent).collect(Collectors.toList()));
        assertEquals(
                List.of(
                        "+вебвизор", "+yandex +вебвизор", "+статистика +слов +яндекс", "+счетчик +метрики", "zyltrc vtnhbrf",
                        "+целевой +звонок|342794051650", "+целевые +визиты", "+карта +кликов", "+метрика +карта +кликов",
                        "+вебвизор +яндекс", "+метрика +вебвизор", "{keyword}", "{keyword}", "40451440019|SEARCH_TOP|c",
                        "42622304363|SEARCH_TOP|c", "43500256001|SEARCH_TOP|c", "43500256001|SEARCH_TOP|c",
                        "43500256041|SEARCH_TOP|c", "43909567400|SEARCH_TOP|c", "43909567800|SEARCH_TOP|c|1"
                ), result.stream().map(ExpenseUploadingRow::utmTerm).collect(Collectors.toList()));
    }

    @Test
    public void testRowsValidation() {
        when(connectorsExpensesStorageMock.load(anyLong(), any(LocalDate.class), anyBoolean()))
                .thenReturn(loadGoogleExpensesYdbRows("partly_valid_rows.tskv").iterator());

        Iterator<ExpenseUploadingRow> it = reportLoader.loadExpensesFromYdb(cabinet);
        List<ExpenseUploadingRow> result = Lists.newArrayList(it);

        assertEquals(13, result.size());
        assertEquals(20, cabinet.getStat().getTotalRowsCount());
        assertEquals(13, cabinet.getStat().getReportRowsCount());
        assertEquals(17, cabinet.getStat().getUtmSourceCount());
        assertEquals(16, cabinet.getStat().getCompatibleDomainCount());

        assertEquals(85, result.stream().map(ExpenseUploadingRow::shows).reduce(Integer::sum).orElseThrow().intValue());
        assertEquals(27, result.stream().map(ExpenseUploadingRow::clicks).reduce(Integer::sum).orElseThrow().intValue());
        assertEquals(487.25, result.stream().map(ExpenseUploadingRow::expenses).reduce(BigDecimal::add).orElseThrow().doubleValue(), 0.0);
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

    private List<GoogleExpensesYdbRow> loadGoogleExpensesYdbRows(String fileName) {
        List<GoogleExpensesYdbRow> result = new ArrayList<>();

        try (
                BufferedReader reader =
                        new BufferedReader(new InputStreamReader(this.getClass().getResourceAsStream("test_data/" + fileName)))
        ) {
            String line;
            while ((line = reader.readLine()) != null) {
                result.add(GoogleExpensesRow.from(line).toYdbRow());
            }
        } catch (Exception e) {
            throw new RuntimeException(e);
        }

        return result;
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
}
