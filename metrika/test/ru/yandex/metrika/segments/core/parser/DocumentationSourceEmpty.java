package ru.yandex.metrika.segments.core.parser;

import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.Set;

import org.jkee.gtree.Forest;

import ru.yandex.metrika.segments.core.doc.AttributeTree2;
import ru.yandex.metrika.segments.core.doc.AttributesDocumentationExternal;
import ru.yandex.metrika.segments.core.doc.DocumentationSource;
import ru.yandex.metrika.segments.core.doc.MetricDocumentationExternal;
import ru.yandex.metrika.segments.core.doc.MetricTree2;
import ru.yandex.metrika.segments.core.meta.AttributeMeta;
import ru.yandex.metrika.segments.core.meta.MetricMeta;
import ru.yandex.metrika.segments.core.schema.TableSchema;

/**
 * Created by orantius on 03.05.16.
 */
public class DocumentationSourceEmpty implements DocumentationSource {

    private AttributesDocumentationExternal ade = new AttributesDocumentationExternal(Collections.emptyList(), Collections.emptyList());
    private MetricDocumentationExternal mde = new MetricDocumentationExternal(Collections.emptyMap());

    @Override
    public AttributesDocumentationExternal getAttributeDocumentationSource() {
        return ade;
    }

    @Override
    public MetricDocumentationExternal getMetricsDocumentationSource() {
        return mde;
    }

    @Override
    public AttributeTree2 buildAttributeTreeDoc(Map<String, AttributeMeta> byName, List<ParamAttributeParser> paramAttributeParsers,
                                                TableSchema tableSchema, String table, Set<String> undocumented, Set<String> undated) {
        return new AttributeTree2(new Forest<>(Collections.emptyList()));
    }

    @Override
    public AttributeTree2 buildAttributeTreeForInterface(Map<String, AttributeMeta> byName, List<ParamAttributeParser> paramAttributeParsers,
                                                         TableSchema tableSchema, String table, Set<String> undocumented, Set<String> undated) {
        return new AttributeTree2(new Forest<>(Collections.emptyList()));
    }

    @Override
    public MetricTree2 buildMetricTreeDoc(Map<String, MetricMeta> byName, String table, Set<String> undocumented, Set<String> undated) {
        return new MetricTree2(new Forest<>(Collections.emptyList()));
    }

    @Override
    public MetricTree2 buildMetricTreeForInterface(Map<String, MetricMeta> byName, String table, Set<String> undocumented, Set<String> undated) {
        return new MetricTree2(new Forest<>(Collections.emptyList()));
    }


}
