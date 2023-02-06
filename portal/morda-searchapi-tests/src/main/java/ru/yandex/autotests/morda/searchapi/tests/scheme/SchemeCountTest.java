package ru.yandex.autotests.morda.searchapi.tests.scheme;

import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.morda.searchapi.client.MordaSearchApi;
import ru.yandex.autotests.morda.searchapi.tests.MordaSearchApiTestsProperties;
import ru.yandex.qatools.allure.annotations.Features;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import static java.lang.String.join;
import static ru.yandex.autotests.morda.searchapi.tests.scheme.SchemeAbstractTest.ValidationCase.validationCase;
import static ru.yandex.autotests.morda.searchapi.tests.scheme.ValidateSchemeUtils.COUNT_BLOCKS;
import static ru.yandex.autotests.morda.searchapi.tests.scheme.ValidateSchemeUtils.langs;
import static ru.yandex.autotests.morda.searchapi.tests.scheme.ValidateSchemeUtils.regions;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 04/06/15
 */
@Aqua.Test(title = "Api Response Scheme Count")
@RunWith(Parameterized.class)
@Features("JSON-schema validation")
public class SchemeCountTest extends SchemeAbstractTest {
    private static final MordaSearchApiTestsProperties CONFIG = new MordaSearchApiTestsProperties();

    public SchemeCountTest(ValidationCase validationCase) {
        super(validationCase);
    }

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> data() throws Exception {
        MordaSearchApi mordaSearchApi = new MordaSearchApi(CONFIG.getMordaSearchApiHost());
        List<Object[]> data = new ArrayList<>();

        langs.forEach(lang ->
                regions.forEach(region ->
                                COUNT_BLOCKS.stream()
                                        .filter(CONFIG.getMordaSearchApiSchemaBlocks()::contains).forEach(block ->
                                                data.add(new Object[]{
                                                                validationCase(
                                                                        join("_", lang, region.toString(), block),
                                                                        mordaSearchApi.getMordaSearchApiV1Req()
                                                                                .withLang(lang)
                                                                                .withBlock(block)
                                                                                .withGeoBySettings(region.getId()),
                                                                        ValidateSchemeUtils.COUNT_SCHEMAS.get(block)
                                                                )
                                                        }

                                                )
                                )
                ));
        return data;
    }

}
