package ru.yandex.autotests.morda.tests.searchapi.stocks;

import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 06/06/16
 */
@RunWith(Parameterized.class)
public class StocksDataTest {
//    protected static final MordaSearchapiTestsProperties CONFIG = new MordaSearchapiTestsProperties();
//
//    @Rule
//    public AllureLoggingRule rule = new AllureLoggingRule();
//
//    protected SearchApiV1Request request;
//    protected SearchApiStocks stocks;
//
//    public StocksDataTest(SearchApiV1Request request) {
//        this.request = request;
//    }
//
//    @Parameterized.Parameters(name = "{0}")
//    public static Collection<SearchApiV1Request> data() {
//        List<SearchApiV1Request> data = new ArrayList<>();
//        MordaClient mordaClient = new MordaClient();
//        URI mordaUri = desktopMain(CONFIG.pages().getEnvironment()).getUrl();
//
//        for (GeobaseRegion region : MordaSearchapiTestsProperties.STOCKS_REGIONS) {
//            SearchApiV1Request request = mordaClient.search().v1(CONFIG.pages().getEnvironment(), STOCKS)
//                    .withGeo(region);
//            data.add(request);
//        }
//
//        return data;
//    }
//
//    @Before
//    public void getStocks() {
//        stocks = request.read().getStocks();
//        assertThat("Котировки не найдены", stocks, notNullValue());
//    }
//
//    @Test
//    public void stocksDiff() {
//        List<SearchApiStocksRow> rows = stocks.getData().getGroups().stream()
//                .filter(e -> !"cash".equals(e.getType()))
//                .flatMap(e -> e.getRows().stream())
//                .collect(Collectors.toList());
//
//        Matcher<SearchApiStocksRow> withDiff = SearchApiStocksRowMatchers.withD(not(isEmptyOrNullString()));
//
//        for (SearchApiStocksRow row : rows) {
//            if (row.getV2() != null && !row.getV2().isEmpty()) {
//                assertThat("Должно быть изменение курса", row, withDiff);
//            }
//        }
//    }
}
