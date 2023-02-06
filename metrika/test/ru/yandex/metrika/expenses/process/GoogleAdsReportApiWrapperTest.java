package ru.yandex.metrika.expenses.process;

import java.time.LocalDate;
import java.util.List;
import java.util.Optional;
import java.util.Set;

import com.google.ads.googleads.lib.GoogleAdsClient;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;

import ru.yandex.metrika.api.management.client.connectors.AdsCabinetEnriched;
import ru.yandex.metrika.api.management.client.connectors.AdsPlatform;
import ru.yandex.metrika.api.management.client.connectors.google.GoogleAdsReportApiWrapper;
import ru.yandex.metrika.api.management.client.connectors.google.GoogleApiRequestType;
import ru.yandex.metrika.managers.Currency;
import ru.yandex.metrika.managers.CurrencyService;
import ru.yandex.metrika.util.log.Log4jSetup;

import static org.junit.Assert.assertTrue;
import static org.mockito.Matchers.anyString;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

public class GoogleAdsReportApiWrapperTest {

    private CurrencyService currencyServiceMock;
    private AdsCabinetEnriched cabinet;
    private Currency currency;
    private GoogleAdsClient client;

    @BeforeClass
    public static void initClass() {
        Log4jSetup.basicSetup();
    }

    @Before
    public void init() {
        currencyServiceMock = mock(CurrencyService.class);
        cabinet = buildCabinet();
        currency = new Currency(643, "RUB", "Российский рубль");
        when(currencyServiceMock.getCurrency(anyString())).thenReturn(Optional.of(currency));
        client = mock(GoogleAdsClient.class);
    }

    @Test
    public void testWithKeywords() {
        GoogleAdsReportApiWrapper wrapper1 = new GoogleAdsReportApiWrapper(client, cabinet, GoogleApiRequestType.WITH_KEYWORDS, null);

        assertTrue(
                wrapper1.getQuery().contains("segments.keyword.info.text") &&
                        wrapper1.getQuery().contains("AND campaign.id IN (10,20,30)")
        );
    }

    @Test
    public void testWithoutKeywords() {
        GoogleAdsReportApiWrapper wrapper = new GoogleAdsReportApiWrapper(client, cabinet, GoogleApiRequestType.WITHOUT_KEYWORDS, null);

        assertTrue(
                !wrapper.getQuery().contains("segments.keyword.info.text") &&
                        wrapper.getQuery().contains("AND campaign.id NOT IN (10,20,30,40,50)")
        );
    }

    @Test
    public void testContentNetwork() {
        GoogleAdsReportApiWrapper wrapper = new GoogleAdsReportApiWrapper(client, cabinet, GoogleApiRequestType.SEARCH_AD_CONTENT_NETWORK, null);

        assertTrue(
                !wrapper.getQuery().contains("segments.keyword.info.text") &&
                        wrapper.getQuery().contains("AND campaign.id IN (30) AND segments.ad_network_type NOT IN (SEARCH,SEARCH_PARTNERS)")
        );
    }

    @Test
    public void testByCampaign() {
        GoogleAdsReportApiWrapper wrapper = new GoogleAdsReportApiWrapper(client, cabinet, GoogleApiRequestType.BY_CAMPAIGN, null);

        assertTrue(
                !wrapper.getQuery().contains("segments.keyword.info.text") &&
                        wrapper.getQuery().contains("AND campaign.id IN (40,50)")
        );
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
        cabinet.setKeywordCampaignIds(List.of(10L, 20L));
        cabinet.setContentNetworkSearchCampaignIds(List.of(30L));
        cabinet.setSmartCampaignIds(List.of(40L));
        cabinet.setPerformanceMaxCampaignIds(List.of(50L));
        return cabinet;
    }
}
