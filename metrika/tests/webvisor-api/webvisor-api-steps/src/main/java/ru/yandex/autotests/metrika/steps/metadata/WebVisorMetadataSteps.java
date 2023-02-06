package ru.yandex.autotests.metrika.steps.metadata;

import org.hamcrest.Matcher;

import ru.yandex.autotests.metrika.beans.schemes.WebvisorV2MetadataDefaultHitDimensionsGETSchema;
import ru.yandex.autotests.metrika.beans.schemes.WebvisorV2MetadataDefaultVisitDimensionsGETSchema;
import ru.yandex.autotests.metrika.beans.schemes.WebvisorV2MetadataHitDimensionsGETSchema;
import ru.yandex.autotests.metrika.beans.schemes.WebvisorV2MetadataVisitDimensionsGETSchema;
import ru.yandex.autotests.metrika.steps.MetrikaBaseSteps;
import ru.yandex.metrika.api.webvisor.WVDimensionMetaExternal;
import ru.yandex.qatools.allure.annotations.Step;

import java.util.List;

import static java.util.stream.Collectors.toList;

/**
 * Created by konkov on 19.01.2015.
 */
public class WebVisorMetadataSteps extends MetrikaBaseSteps {

    private static final String WEBVISOR_DEFAULT_HIT_DIMENSIONS_PATH = "/webvisor/v2/metadata/default_hit_dimensions";
    private static final String WEBVISOR_DEFAULT_VISIT_DIMENSIONS_PATH = "/webvisor/v2/metadata/default_visit_dimensions";
    private static final String WEBVISOR_HIT_DIMENSIONS_PATH = "/webvisor/v2/metadata/hit_dimensions";
    private static final String WEBVISOR_VISIT_DIMENSIONS_PATH = "/webvisor/v2/metadata/visit_dimensions";

    private List<WVDimensionMetaExternal> getWebVisorVisitDimensionsRaw() {
        return getResponse(WEBVISOR_VISIT_DIMENSIONS_PATH)
                .readResponse(WebvisorV2MetadataVisitDimensionsGETSchema.class).getResponse();
    }

    @Step("Получить список измерений вебвизора для визита")
    public List<String> getWebVisorVisitDimensions() {
        return getWebVisorVisitDimensionsRaw().stream().map(WVDimensionMetaExternal::getDim).collect(toList());
    }

    @Step("Получить список фильтруемых измерений вебвизора для визита")
    public List<String> getWebVisorVisitFilterableDimensions() {
        return getWebVisorVisitDimensionsRaw().stream()
                .filter(WVDimensionMetaExternal::getAllowFilters)
                .map(WVDimensionMetaExternal::getDim)
                .collect(toList());
    }

    @Step("Получить сегмент для измерения {0} вебвизора для визита")
    public String getWebvisorDimensionSegment(String dimension) {
        WVDimensionMetaExternal dim = getWebVisorVisitDimensionsRaw().stream()
                .filter(d -> d.getDim().equals(dimension)).findFirst().get();
        if (dim.getAllowFilters() == true) {
            return dim.getDim();
        } else {
            return dim.getSegment();
        }
    }

    @Step("Получить сортируемые измерения вебвизора для визита c типом {0}")
    public List<String> getWebVisorVisitSortableDimensions(Matcher<String> typeMatcher) {
        return getWebVisorVisitDimensionsRaw().stream()
                .filter(x -> x.getAllowSort() && typeMatcher.matches(x.getType()))
                .map(WVDimensionMetaExternal::getDim)
                .collect(toList());
    }

    private List<WVDimensionMetaExternal> getWebVisorHitDimensionsRaw() {
        return getResponse(WEBVISOR_HIT_DIMENSIONS_PATH)
                .readResponse(WebvisorV2MetadataHitDimensionsGETSchema.class).getResponse();
    }

    @Step("Получить список измерений вебвизора для просмотра")
    public List<String> getWebVisorHitDimensions() {
        return getWebVisorHitDimensionsRaw().stream().map(WVDimensionMetaExternal::getDim).collect(toList());
    }

    @Step("Получить список измерений вебвизора по умолчанию для визита")
    public WebvisorV2MetadataDefaultVisitDimensionsGETSchema getWebVisorDefaultVisitDimensions() {
        return getResponse(WEBVISOR_DEFAULT_VISIT_DIMENSIONS_PATH)
                .readResponse(WebvisorV2MetadataDefaultVisitDimensionsGETSchema.class);
    }

    @Step("Получить список измерений вебвизора по умолчанию для просмотра")
    public WebvisorV2MetadataDefaultHitDimensionsGETSchema getWebVisorDefaultHitDimensions() {
        return getResponse(WEBVISOR_DEFAULT_HIT_DIMENSIONS_PATH)
                .readResponse(WebvisorV2MetadataDefaultHitDimensionsGETSchema.class);
    }
}
