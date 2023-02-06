package ru.yandex.autotests.morda.searchapi.tests.scheme;

import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.morda.region.Region;
import ru.yandex.autotests.morda.searchapi.client.MordaSearchApi;
import ru.yandex.autotests.morda.searchapi.tests.MordaSearchApiTestsProperties;
import ru.yandex.qatools.allure.annotations.Features;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import static java.lang.String.join;
import static java.util.Arrays.asList;
import static ru.yandex.autotests.morda.searchapi.tests.scheme.SchemeAbstractTest.ValidationCase.validationCase;
import static ru.yandex.autotests.morda.searchapi.tests.scheme.ValidateSchemeUtils.langs;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 04/06/15
 */
@Aqua.Test(title = "Api Response Scheme")
@RunWith(Parameterized.class)
@Features("JSON-schema validation")
public class SchemeTest extends SchemeAbstractTest {
    private static final MordaSearchApiTestsProperties CONFIG = new MordaSearchApiTestsProperties();

    public SchemeTest(ValidationCase validationCase) {
        super(validationCase);
    }

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> data() {
        MordaSearchApi mordaSearchApi = new MordaSearchApi(CONFIG.getMordaSearchApiHost());
        List<Object[]> data = new ArrayList<>();

        langs.forEach(lang ->
                asList(Region.values()).forEach(region ->
                                CONFIG.getMordaSearchApiSchemaBlocks().forEach(block ->
                                                data.add(new Object[]{
                                                                validationCase(
                                                                        join("_", lang, region.toString(), block),
                                                                        mordaSearchApi.getMordaSearchApiV1Req()
                                                                                .withLang(lang)
                                                                                .withBlock(block)
                                                                                .withGeoBySettings(region.getId()),
                                                                        ValidateSchemeUtils.TEST_SCHEMAS.get(block)
                                                                )
                                                        }

                                                )
                                )
                ));
        return data;
    }
}
