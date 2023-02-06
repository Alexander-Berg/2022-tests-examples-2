package ru.yandex.metrika.segments.core.parser;

import java.util.List;

import gnu.trove.map.hash.TObjectLongHashMap;
import org.apache.logging.log4j.Level;
import org.jetbrains.annotations.NotNull;

import ru.yandex.metrika.rbac.EmptyRankProvider;
import ru.yandex.metrika.segments.core.ApiUtils;
import ru.yandex.metrika.segments.core.bundles.SimpleProvidersBundle;
import ru.yandex.metrika.segments.core.bundles.UnionBundle;
import ru.yandex.metrika.segments.site.RequiredFilterBuilderSite;
import ru.yandex.metrika.segments.site.RowsUniquesProvider;
import ru.yandex.metrika.segments.site.SamplerSite;
import ru.yandex.metrika.util.locale.LocaleDictionaries;
import ru.yandex.metrika.util.log.Log4jSetup;

public class SimpleTestSetup {

    private final SimpleTestAttributeBundle bundle = new SimpleTestAttributeBundle();

    private final ApiUtils apiUtils;

    private final QueryParserFactory queryParserFactory;

    public SimpleTestSetup() throws Exception {
        Log4jSetup.basicSetup(Level.DEBUG);
        SimpleTestTableSchema tableSchema = new SimpleTestTableSchema();
        apiUtils = new ApiUtils();
        SimpleProvidersBundle providersBundle = new SimpleProvidersBundle();
        providersBundle.setRequiredFilterBuilder(getRequiredFilterBuilder());
        providersBundle.setLocaleDictionaries(new LocaleDictionaries());
        providersBundle.afterPropertiesSet();
        apiUtils.setProvidersBundle(providersBundle);
        apiUtils.setTableSchema(tableSchema);
        apiUtils.setAttributeParams(SimpleTestAttributeBundle.attributeParams);
        apiUtils.setBundleFactory(()->new UnionBundle(List.of(bundle)));
        apiUtils.setDocumentationSource(new DocumentationSourceEmpty());
        apiUtils.afterPropertiesSet();

        SamplerSite samplerSite = new SamplerSite(new TObjectLongHashMap<>(), new TObjectLongHashMap<>(), new TObjectLongHashMap<>(), new RowsUniquesProvider() {});
        apiUtils.setSampler(samplerSite);

        queryParserFactory = apiUtils.getParserFactory();
        queryParserFactory.setAppendNonZeroRowsFilter(false);
    }

    @NotNull
    private RequiredFilterBuilderSite getRequiredFilterBuilder() {
        RequiredFilterBuilderSite requiredFilterBuilderSite = new RequiredFilterBuilderSite();
        requiredFilterBuilderSite.setRankProvider(new EmptyRankProvider());
        return requiredFilterBuilderSite;
    }

    public ApiUtils getApiUtils() {
        return apiUtils;
    }

    public QueryParserFactory getQueryParserFactory() {
        return queryParserFactory;
    }

    public SimpleTestAttributeBundle getBundle() {
        return bundle;
    }
}
