package ru.yandex.metrika.segments;

import java.util.function.Supplier;

import com.google.common.collect.Lists;
import org.junit.Ignore;

import ru.yandex.metrika.segments.core.bundles.AttributeBundle;
import ru.yandex.metrika.segments.core.bundles.UnionBundle;
import ru.yandex.metrika.segments.core.doc.DocumentationSource;
import ru.yandex.metrika.segments.site.bundles.clicks.ClickStorageAttributeBundle;
import ru.yandex.metrika.segments.site.bundles.clicks.ClicksAttributeBundle;
import ru.yandex.metrika.segments.site.bundles.clicks.VisitClickJoinAttributes;
import ru.yandex.metrika.segments.site.bundles.hits.HitAttributes;
import ru.yandex.metrika.segments.site.bundles.providers.VisitProvidersBundle;
import ru.yandex.metrika.segments.site.bundles.visits.VisitAttributes;
import ru.yandex.metrika.segments.site.schema.TableSchemaSite;

/**
 * это вообще не тест, но т.к. он лежит в тестах и имеет в названии Test
 * то его всем очень хочется запустить как тест.
 */
@Ignore
public class TestJoinBundleFactory implements Supplier<UnionBundle> {

    private final TableSchemaSite tableSchema;
    private final VisitProvidersBundle visitProvidersBundle;
    private final DocumentationSource documentationSource;
    private final ClicksAttributeBundle clicksAttributeBundle;
    private VisitAttributes visitAttributes;
    private HitAttributes hitAttributes;
    private ClickStorageAttributeBundle clickStorageAttributeBundle;

    public TestJoinBundleFactory(TableSchemaSite tableSchema,
                                 VisitProvidersBundle visitProvidersBundle,
                                 DocumentationSource documentationSource) {
        this.tableSchema = tableSchema;
        this.visitProvidersBundle = visitProvidersBundle;
        this.documentationSource = documentationSource;
        visitAttributes = new VisitAttributes(tableSchema, visitProvidersBundle, documentationSource);
        hitAttributes = new HitAttributes(tableSchema, visitProvidersBundle, documentationSource);
        clickStorageAttributeBundle = new ClickStorageAttributeBundle(tableSchema, visitProvidersBundle, documentationSource);
        clicksAttributeBundle = new ClicksAttributeBundle(tableSchema, visitProvidersBundle, documentationSource);
    }


    @Override
    public UnionBundle get() {
        UnionBundle bundle = new UnionBundle(Lists.newArrayList(
                // если их не добавить, то не работают getSqlGenerator() для спрятанных в joined attribute атрибутов.
                visitAttributes,
                hitAttributes,
                clicksAttributeBundle,
                clickStorageAttributeBundle,
                new VisitClickJoinAttributes(
                        new ClickStorageAttributeBundle(tableSchema, visitProvidersBundle, documentationSource),
                        new ClicksAttributeBundle(tableSchema, visitProvidersBundle, documentationSource),
                        visitProvidersBundle, documentationSource
                )
        ));
        bundle.postInit();
        return bundle;
    }

    public AttributeBundle getVisitAttributes() {
        return visitAttributes;
    }

    public AttributeBundle getHitAttributes() {
        return hitAttributes;
    }
}
