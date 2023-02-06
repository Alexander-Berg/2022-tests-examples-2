package ru.yandex.autotests.morda.searchapi.tests.oauth;

import com.fasterxml.jackson.core.JsonProcessingException;
import org.junit.Test;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.morda.region.Region;
import ru.yandex.autotests.morda.searchapi.beans.informer.MordaSearchApiInformerDataItem;
import ru.yandex.autotests.morda.searchapi.client.MordaSearchApi;
import ru.yandex.autotests.morda.searchapi.client.requests.MordaSearchApiV1Request;
import ru.yandex.autotests.morda.searchapi.tests.MordaSearchApiTestsProperties;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import java.util.Optional;

import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.greaterThanOrEqualTo;
import static org.hamcrest.Matchers.is;
import static org.hamcrest.Matchers.notNullValue;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 30/06/15
 */
@Aqua.Test(title = "Informer Mail Count")
@Features("OAuth")
@Stories("Informer Mail Count")
public class InformerMailCountTest {

    private static final MordaSearchApiTestsProperties CONFIG = new MordaSearchApiTestsProperties();

    @Test
    public void mailCount() throws JsonProcessingException {

        MordaSearchApi mordaSearchApi = new MordaSearchApi(CONFIG.getMordaSearchApiHost());

        MordaSearchApiV1Request request = mordaSearchApi.getMordaSearchApiV1Req()
                .withBlock("informer")
                .withGeoBySettings(Region.MOSCOW.getId())
                .withOauth("cf66df4971454e52ac376658cd90bebf")
                .build();

        Optional<MordaSearchApiInformerDataItem> mail = request.read().getInformer().getData()
                .getList().stream()
                .filter(e -> e.getId().equals("mail"))
                .findFirst();

        assertThat("Блок почты отсутствует", mail.isPresent(), is(true));
        assertThat("Количество писем в блоке почты отсутствует", mail.get().getN(), notNullValue());
        assertThat("Неверное количество писем в почте", mail.get().getN().getValue(), greaterThanOrEqualTo(0));
    }

}
