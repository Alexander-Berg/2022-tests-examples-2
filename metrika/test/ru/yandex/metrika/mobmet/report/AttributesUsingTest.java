package ru.yandex.metrika.mobmet.report;

import java.util.Arrays;
import java.util.Collections;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.stream.Collectors;
import java.util.stream.Stream;

import com.google.common.collect.Sets;
import org.assertj.core.util.Preconditions;
import org.junit.Test;

import ru.yandex.metrika.api.constructor.response.DimensionMetaExternal;
import ru.yandex.metrika.locale.LangCodes;
import ru.yandex.metrika.mobmet.controller.ConstructorMetaController;
import ru.yandex.metrika.mobmet.report.generator.ReportParamConverter;
import ru.yandex.metrika.mobmet.report.generator.ReportParamTarget;
import ru.yandex.metrika.mobmet.report.generator.ReportParamsConverters;
import ru.yandex.metrika.mobmet.report.generator.ReportParamsTargets;
import ru.yandex.metrika.mobmet.report.generator.SegmentGenerator;
import ru.yandex.metrika.mobmet.report.generator.destination.ExistsParamTarget;
import ru.yandex.metrika.mobmet.report.generator.destination.FlatParamTarget;
import ru.yandex.metrika.segments.apps.bundles.AppAttributeParams;
import ru.yandex.metrika.segments.apps.bundles.MobileProvidersBundle;
import ru.yandex.metrika.segments.apps.bundles.MobmetBundleFactory;
import ru.yandex.metrika.segments.apps.bundles.funnels.param.FunnelPatternParamMetaFactory;
import ru.yandex.metrika.segments.apps.bundles.funnels.param.FunnelRestrictionParamMetaFactory;
import ru.yandex.metrika.segments.apps.doc.DocumentationSourceApps;
import ru.yandex.metrika.segments.apps.meta.ConstructorMetaGeneratorApps;
import ru.yandex.metrika.segments.apps.misc.PartnerTypes;
import ru.yandex.metrika.segments.apps.schema.MobmetTableSchema;
import ru.yandex.metrika.segments.apps.type.LocalTypesApps;
import ru.yandex.metrika.segments.core.ApiUtils;
import ru.yandex.metrika.segments.core.schema.TableMeta;
import ru.yandex.metrika.util.collections.Lists2;
import ru.yandex.metrika.util.locale.LocaleDictionaries;

import static org.junit.Assert.assertEquals;


/**
 * Проверяем, что всё, что используется в сегментации будет проверено в интеграционных тестах
 */
public class AttributesUsingTest {

    @Test
    public void test() throws Exception {

        Set<String> metaAttributes = getTestMetaAttributes();
        Set<String> segmentationAttributes = getSegmentationAttributes();

        Set<String> difference = Sets.difference(segmentationAttributes, metaAttributes);

        assertEquals("Все атрибуты используемые в сегментации должны быть описаны в мете для тестов",
                Collections.emptySet(), difference);
    }

    private Set<String> getTestMetaAttributes() throws Exception {

        LocaleDictionaries localeDictionaries = new LocaleDictionaries();
        localeDictionaries.afterPropertiesSet();
        LangCodes langCodes = new LangCodes();
        langCodes.setLocaleDictionaries(localeDictionaries);
        LocalTypesApps localTypesApps = new LocalTypesApps(localeDictionaries, null, null);

        ApiUtils apiUtils = new ApiUtils();

        FunnelPatternParamMetaFactory funnelsParamMetaFactory = new FunnelPatternParamMetaFactory(apiUtils);
        FunnelRestrictionParamMetaFactory funnelRestrictionParamMetaFactory = new FunnelRestrictionParamMetaFactory(apiUtils);
        AppAttributeParams attributeParams = new AppAttributeParams(funnelsParamMetaFactory, funnelRestrictionParamMetaFactory);

        MobileProvidersBundle bundle = new MobileProvidersBundle();
        bundle.setAttributeParams(attributeParams);
        bundle.setLangCodes(langCodes);
        bundle.setLocaleDictionaries(localeDictionaries);
        bundle.setLocalTypesApps(localTypesApps);
        bundle.setPartnerTypes(new PartnerTypes());

        MobmetTableSchema tableSchema = new MobmetTableSchema();
        DocumentationSourceApps docSource = new DocumentationSourceApps();
        MobmetBundleFactory bundleFactory = new MobmetBundleFactory(tableSchema, bundle, docSource);

        apiUtils.setProvidersBundle(bundle);
        apiUtils.setBundleFactory(bundleFactory);
        apiUtils.setTableSchema(tableSchema);
        apiUtils.setDocumentationSource(docSource);
        apiUtils.setAttributeParams(attributeParams);

        apiUtils.afterPropertiesSet();


        ConstructorMetaGeneratorApps metaGenerator = new ConstructorMetaGeneratorApps(apiUtils, tableSchema, docSource);
        ConstructorMetaController metaController = new ConstructorMetaController(metaGenerator, null);
        return metaController.getDocumentedAttributes(null, false).getResponse().getAttributes().stream()
                .map(DimensionMetaExternal::getDim)
                .collect(Collectors.toSet());
    }

    /**
     * Dimension-ы, используемые в сегментации
     */
    private Set<String> getSegmentationAttributes() {
        Map<ReportType, SegmentGenerator> generators =
                new SegmentGeneratorsFactory(SegmentGeneratorMocks.emptyPushMetaService()).build();

        Set<String> result = new HashSet<>();

        generators.forEach((reportType, generator) -> {
            ReportParamsConverters converters = generator.getParamsConverters();
            ReportParamsTargets targets = generator.getParamsTargets();

            Arrays.stream(ReportParam.values()).forEach(reportParam -> {
                Optional<ReportParamTarget> target = targets.get(reportParam);
                target.ifPresent(t -> {
                    ReportParamConverter<?> converter = converters.get(reportParam);
                    result.addAll(extractGeneratorsAttributes(reportType, t, converter));
                });
            });
        });
        return result;
    }

    /**
     * Ходим по мете и пытаемся понять какие атрибуты используются
     */
    private List<String> extractGeneratorsAttributes(ReportType reportType,
                                                     ReportParamTarget target,
                                                     ReportParamConverter<?> converter) {
        if (target.shouldSkip()) {
            return Collections.emptyList();
        }

        List<String> namespaces = reportType.getAppTables().stream()
                .map(TableMeta::getNamespace)
                .collect(Collectors.toList());

        if (target.getOrigin() instanceof FlatParamTarget) {
            return converter.getUsedAttributes().stream()
                    .flatMap(a -> namespaces.stream().map(ns -> addNamespace(ns, a)))
                    .collect(Collectors.toList());
        }

        if (target.getOrigin() instanceof ExistsParamTarget) {
            ExistsParamTarget existsTarget = (ExistsParamTarget) target.getOrigin();

            String existsNamespace = existsTarget.getTable().getNamespace();

            List<String> converterAttributes = converter.getUsedAttributes().stream()
                    .map(a -> addNamespace(existsNamespace, a))
                    .collect(Collectors.toList());

            // Сами атрибуты, которые используются в exist-ах, должны быть в обоих namespace-ах
            List<String> existsAttributes = existsTarget.getUsedAttributes().stream()
                    .flatMap(a -> Lists2.concat(existsNamespace, namespaces)
                            .stream()
                            .map(ns -> addNamespace(ns, a)))
                    .collect(Collectors.toList());

            return Stream.concat(converterAttributes.stream(), existsAttributes.stream())
                    .distinct()
                    .collect(Collectors.toList());
        }

        throw new IllegalStateException("Unexpected target: " + target.getOrigin().getClass());
    }

    private String addNamespace(String namespace, String attribute) {
        Preconditions.checkNotNull(attribute);
        return namespace + attribute;
    }
}
