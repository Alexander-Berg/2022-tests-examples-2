package ru.yandex.autotests.metrika.steps.metadata;

import ru.yandex.autotests.irt.testutils.json.JsonUtils;
import ru.yandex.autotests.metrika.beans.schemes.StatV1MetadataPresetsGETSchema;
import ru.yandex.autotests.metrika.converters.LegacyPresetConverter;
import ru.yandex.autotests.metrika.core.response.MetrikaJsonResponse;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.metadata.legacy.LegacyPresetWrapper;
import ru.yandex.autotests.metrika.steps.MetrikaBaseSteps;
import ru.yandex.autotests.metrika.utils.AllureUtils;
import ru.yandex.qatools.allure.annotations.Step;

import java.util.*;

import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.on;
import static ch.lambdaj.collection.LambdaCollections.with;
import static org.apache.commons.lang3.ArrayUtils.toArray;
import static org.apache.commons.lang3.StringUtils.EMPTY;
import static org.hamcrest.Matchers.*;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assumeThat;
import static ru.yandex.autotests.metrika.data.common.counters.Counter.GOAL_ID;

/**
 * Created by konkov on 19.01.2015.
 */
public class LegacyMetadataSteps extends MetrikaBaseSteps {

    private static final String LEGACY_PRESETS_PATH = "/internal/metrage/stat/v1/metadata/presets";

    private static final List<String> REQUIRE_GOAL_ID = Collections.singletonList("ecommerce");

    public void attachPreset(LegacyPresetWrapper preset) {
        String presetLabel = "Шаблон";
        AllureUtils.addTestParameter(presetLabel, preset.toString());
        AllureUtils.addJsonAttachment(presetLabel, JsonUtils.toString(preset.getPreset()));
    }

    @Step("Получить список всех шаблонов legacy API")
    public List<LegacyPresetWrapper> getAllLegacyPresets() {
        MetrikaJsonResponse response = getResponse(LEGACY_PRESETS_PATH);

        List<LegacyPresetWrapper> presets = with(response.readResponse(StatV1MetadataPresetsGETSchema.class).getPresets())
                .convert(new LegacyPresetConverter());

        assumeThat("для тестов доступен список шаблонов",
                presets,
                not(empty()));

        return presets;
    }

    @Step("Получить список параметров тестов со счетчиками {0}")
    public Collection<Object[]> getPresetCounterGoalParameters(List<Counter> counters) {
        List<Object[]> parameters = new ArrayList<>();

        for (LegacyPresetWrapper legacyPresetWrapper : getAllLegacyPresets()) {
            parameters.addAll(combinePresetWithCounters(counters, legacyPresetWrapper));
        }

        return parameters;
    }


    @Step("Получить список параметров тестов со счетчиками {0} для отчета 'drill down'")
    public Collection<Object[]> getPresetCounterGoalDrillDownParameters(List<Counter> counters) {
        List<Object[]> parameters = new ArrayList<>();

        //создаем параметр теста, только если в пресете более одного измерения
        //аналогично интерфейсу, который соответствующую кнопку показывает тоже по этому условию
        for (LegacyPresetWrapper legacyPresetWrapper :
                with(getAllLegacyPresets()).retain(having(
                        on(LegacyPresetWrapper.class).getPreset().getDimensions(),
                        hasSize(greaterThan(1))))) {
            parameters.addAll(combinePresetWithCounters(counters, legacyPresetWrapper));
        }

        return parameters;
    }

    private List<Object[]> combinePresetWithCounters(List<Counter> counters, LegacyPresetWrapper legacyPresetWrapper) {

        List<Object[]> parameters = new ArrayList<>();

        for (Counter counter : counters) {
            if (!REQUIRE_GOAL_ID.contains(legacyPresetWrapper.getPreset().getName())) {
                parameters.add(toArray(legacyPresetWrapper, counter, EMPTY));
            }

            /*if (legacyPresetWrapper.getPreset().getEnableGoal()) {
                parameters.add(toArray(legacyPresetWrapper, counter,
                        Objects.toString(counter.get(GOAL_ID), EMPTY)));
            }*/
        }

        return parameters;
    }
}
