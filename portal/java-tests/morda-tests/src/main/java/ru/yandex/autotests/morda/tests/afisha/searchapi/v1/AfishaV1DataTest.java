package ru.yandex.autotests.morda.tests.afisha.searchapi.v1;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.JsonNodeType;
import com.fasterxml.jackson.databind.node.ObjectNode;
import org.hamcrest.Matcher;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.morda.api.search.SearchApiRequestData;
import ru.yandex.autotests.morda.api.search.v1.SearchApiV1Request;
import ru.yandex.autotests.morda.beans.api.search.v1.afisha.AfishaApiV1;
import ru.yandex.autotests.morda.beans.api.search.v1.afisha.AfishaApiV1Data;
import ru.yandex.autotests.morda.beans.api.search.v1.afisha.AfishaApiV1DataMatchers;
import ru.yandex.autotests.morda.beans.api.search.v1.afisha.AfishaApiV1Event;
import ru.yandex.autotests.morda.beans.api.search.v1.afisha.AfishaApiV1EventMatchers;
import ru.yandex.autotests.morda.data.afisha.AfishaBlockData;
import ru.yandex.autotests.morda.data.afisha.searchapi.AfishaSearchApiData;
import ru.yandex.autotests.morda.matchers.AllOfDetailedMatcher;
import ru.yandex.autotests.morda.steps.attach.AttachmentUtils;
import ru.yandex.autotests.morda.tests.MordaTestTags;
import ru.yandex.autotests.morda.tests.MordaTestsProperties;
import ru.yandex.geobase.regions.GeobaseRegion;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Step;

import java.util.Collection;
import java.util.List;

import static java.util.Arrays.asList;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.autotests.morda.data.afisha.AfishaBlockData.getAfishaRegion;
import static ru.yandex.autotests.morda.matchers.AllOfDetailedMatcher.allOfDetailed;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 14/08/16
 */
@Aqua.Test(title = MordaTestTags.AFISHA)
@Features({MordaTestTags.SEARCH_API, MordaTestTags.V1, MordaTestTags.AFISHA})
@RunWith(Parameterized.class)
public class AfishaV1DataTest {
    private static final MordaTestsProperties CONFIG = new MordaTestsProperties();

    private AfishaSearchApiData data = new AfishaSearchApiData();
    private SearchApiV1Request request;
    private SearchApiRequestData requestData;

    public AfishaV1DataTest(SearchApiV1Request request) {
        this.request = request;
        this.requestData = request.getRequestData();
    }

    @Parameterized.Parameters(name = "{0}")
    public static Collection<SearchApiV1Request> data() {
        return AfishaV1TestCases.getData(CONFIG.pages().getEnvironment()).subList(0, 1);
    }

    @Test
    public void afishaData() throws JsonProcessingException {
        AfishaApiV1 afisha = request.read().getAfisha();
        checkAfisha(afisha);
    }


    public void checkAfisha(AfishaApiV1 afisha) throws JsonProcessingException {
        checkAfishaExists(afisha);
        checkAfishaData(afisha.getData());

//        assertThat(afisha.getData(), getAfishaDataMatcher());

//        assertThat(afisha, allOfDetailed(
////                hasPropertyWithValue(on(Afisha.class).getTitle(), equalTo())
//                AfishaMatchers.withData(getAfishaDataMatcher())
//        ));
    }

    @Step("Check afisha exists")
    public void checkAfishaExists(AfishaApiV1 afisha) {

    }

    @Step("Check afisha data")
    public void checkAfishaData(AfishaApiV1Data afishaData) throws JsonProcessingException {
        checkBean(afishaData, getAfishaDataMatcher());
        checkAfishaEvents(afishaData.getEvents());
    }

    @Step("Check afisha events")
    public void checkAfishaEvents(List<AfishaApiV1Event> afishaEvents) throws JsonProcessingException {
        for (int i = 0; i != afishaEvents.size(); i++) {
            checkAfishaEvent(i, afishaEvents.get(i));
        }
    }

    @Step("Check afisha event {0}")
    public void checkAfishaEvent(int pos, AfishaApiV1Event afishaEvent) throws JsonProcessingException {
        checkBean(afishaEvent, allOfDetailed(
                AfishaApiV1EventMatchers.withPoster(data.getPosterUrlMatcher(AfishaBlockData.AfishaPosterSize._960x960_noncrop))
        ));
    }


    public Matcher<AfishaApiV1Data> getAfishaDataMatcher() {
        GeobaseRegion afishaRegion = getAfishaRegion(requestData.getGeo(), requestData.getLanguage());

        AllOfDetailedMatcher<AfishaApiV1Data> matcher = allOfDetailed(
                AfishaApiV1DataMatchers.withGeo(equalTo(afishaRegion.getRegionId())),
                AfishaApiV1DataMatchers.withUrl(data.getUrlMatcher(requestData.getGeo(), requestData.getLanguage()))
        );

        if (afishaRegion.getRegionId() != requestData.getGeo().getRegionId()) {
            String afishaRegionName = afishaRegion.getTranslations(requestData.getLanguage().getValue()).getNominativeCase();
            matcher.and(AfishaApiV1DataMatchers.withCity(equalTo(afishaRegionName)));
        }

        System.out.println(matcher);

        return matcher;
    }


    public <T> void checkBean(T object, Matcher<? super T> matcher) throws JsonProcessingException {
        JsonNode node = new ObjectMapper().convertValue(object, JsonNode.class);

        ObjectNode tmpNode = node.deepCopy();

        List<JsonNodeType> removeTypes = asList(JsonNodeType.ARRAY, JsonNodeType.OBJECT, JsonNodeType.POJO);

        tmpNode.fieldNames().forEachRemaining(e -> {
            JsonNodeType eType = tmpNode.get(e).getNodeType();
            if (removeTypes.contains(eType)) {
                tmpNode.remove(e);
                tmpNode.put(e, "[" + eType.toString().toLowerCase() + " removed]");
            }
        });

        String attach = new ObjectMapper().writerWithDefaultPrettyPrinter().writeValueAsString(tmpNode) + "\n\n***** CHECK: ***** \n" + matcher.toString();


        System.out.println(attach);

        AttachmentUtils.attachText("check.info", attach);

        assertThat(object, matcher);
    }


}
