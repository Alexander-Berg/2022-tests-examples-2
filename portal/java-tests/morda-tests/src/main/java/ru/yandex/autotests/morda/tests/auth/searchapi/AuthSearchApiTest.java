package ru.yandex.autotests.morda.tests.auth.searchapi;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 19/09/16
 */
public abstract class AuthSearchApiTest {//extends AuthTest {

//    protected InformerSearchApiChecker informerChecker = informerSearchApiChecker(getVersion(), null, null);
//    protected SearchApiV1Request baseRequest = client.search().v1(getVersion(), CONFIG.pages().getEnvironment(), INFORMER)
//            .withGeo(Russia.SAINT_PETERSBURG)
//            .withLanguage(MordaLanguage.UK);
//
//    private static SearchApiInformerItem getListItem(SearchApiInformer informer, String id) {
//        Optional<SearchApiInformerItem> optionalItem = informer.getData().getList().stream()
//                .filter(e -> e.getId().equals(id))
//                .findAny();
//        assertTrue("Failed to get item with id \"" + id + "\"", optionalItem.isPresent());
//        SearchApiInformerItem item = optionalItem.get();
//        assertThat("Item with id \"" + id + "\" is null", item, notNullValue());
//        return item;
//    }
//
//    @Step("Should be not authorized")
//    protected void shouldBeAuthorized(MordaSearchApiResponse response) {
//        assertTrue(isAuthorized(response));
//    }
//
//    @Step("Should be not authorized")
//    protected void shouldBeNotAuthorized(MordaSearchApiResponse response) {
//        assertFalse(isAuthorized(response));
//    }
//
//    protected boolean isAuthorized(MordaSearchApiResponse response) {
//        informerChecker.checkExists(response);
//        SearchApiInformer informer = response.getInformer();
//        SearchApiInformerItem mail = getListItem(informer, "mail");
//        return mail.getN() != null;
//    }
//
//    protected abstract MordaSearchApiVersion getVersion();
//
//    @Test
//    public void noAuthWithoutToken() {
//        MordaSearchApiResponse searchApi = baseRequest.read();
//
//        shouldBeNotAuthorized(searchApi);
//    }
//
//    @Test
//    public void noAuthWithBadToken() {
//        MordaSearchApiResponse searchApi = baseRequest
//                .withOauth(RandomStringUtils.randomAlphanumeric(20))
//                .read();
//
//        shouldBeNotAuthorized(searchApi);
//    }
//
//    @Test
//    public void authWithToken() {
//        MordaSearchApiResponse searchApi = baseRequest
//                .withOauth("cf66df4971454e52ac376658cd90bebf")
//                .read();
//
//        shouldBeAuthorized(searchApi);
//    }
}
