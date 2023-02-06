package ru.yandex.metrika.common.test.medium;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.function.Consumer;
import java.util.function.Supplier;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;

import ru.yandex.autotests.metrika.commons.beans.Column;
import ru.yandex.bolts.collection.Cf;
import ru.yandex.bolts.collection.ListF;
import ru.yandex.bolts.collection.MapF;
import ru.yandex.inside.yt.kosher.Yt;
import ru.yandex.inside.yt.kosher.cypress.YPath;
import ru.yandex.inside.yt.kosher.impl.YtUtils;
import ru.yandex.inside.yt.kosher.impl.ytree.builder.YTreeBuilder;
import ru.yandex.inside.yt.kosher.impl.ytree.object.annotation.YTreeField;
import ru.yandex.inside.yt.kosher.tables.YTableEntryTypes;
import ru.yandex.inside.yt.kosher.ytree.YTreeNode;
import ru.yandex.yt.ytclient.tables.TableSchema;

import static java.lang.String.join;
import static java.util.Arrays.stream;
import static java.util.stream.Collectors.toList;
import static org.apache.commons.lang3.StringUtils.isNotBlank;
import static org.awaitility.Awaitility.await;
import static org.awaitility.Duration.TEN_SECONDS;
import static org.awaitility.Duration.TWO_HUNDRED_MILLISECONDS;
import static ru.yandex.bolts.collection.Cf.map;
import static ru.yandex.bolts.collection.Cf.wrap;
import static ru.yandex.inside.yt.kosher.cypress.CypressNodeType.MAP;
import static ru.yandex.inside.yt.kosher.cypress.CypressNodeType.TABLE;
import static ru.yandex.inside.yt.kosher.cypress.YPath.simple;
import static ru.yandex.inside.yt.kosher.impl.ytree.builder.YTree.stringNode;

@Component
public class YtClient {

    private static final Logger log = LoggerFactory.getLogger(YtClient.class);

    private final Yt yt;

    public YtClient() {
        this.yt = YtUtils.http(System.getenv().getOrDefault("YT_PROXY", "localhost:8000"), "");
    }

    public static String buildYtPath(String root, String... subNodes) {
        return join("/", root, join("/", subNodes));
    }

    public <T> void createDynamicTable(String path, Class<T> contentClass) {
        createDynamicTable(path, contentClass, null);
    }

    public <T> void createDynamicTable(String path, Class<T> contentClass, Map<String, String> additionalAttributes) {
        var node = new YTreeBuilder().value(getSchemaFromClass(contentClass)).build();
        createDynamicTable(path, node, additionalAttributes);
    }

    public <T> void createDynamicTable(String path, TableSchema schema) {
        createDynamicTable(path, schema.toYTree(), null);
    }

    private <T> void createDynamicTable(String path, YTreeNode schema, Map<String, String> additionalAttributes) {
        MapF<String, YTreeNode> attributes = Cf.hashMap();
        attributes.put("dynamic", new YTreeBuilder().value(true).build());
        attributes.put("schema", schema);
        if (additionalAttributes != null) {
            additionalAttributes.forEach((key, value) -> attributes.put(key, stringNode(value)));
        }

        yt.cypress().create(simple(path), TABLE, true, false, attributes);
        yt.tables().mount(simple(path));
        waitMounted(simple(path));
    }

    public void createMapNode(String path) {
        createMapNode(path, false);
    }

    public void createMapNode(String path, boolean ignoreExisting) {
        yt.cypress().create(simple(path), MAP, true, ignoreExisting);
    }

    public void clearMapNode(String path) {
        removeSubNodes(path);
        createMapNode(path, true);
    }

    private void removeSubNodes(String path) {
        if (yt.cypress().exists(simple(path))) {
            yt.cypress().list(simple(path))
                    .forEach(yTreeStringNode -> yt.cypress()
                            .remove(simple(join("/", path, yTreeStringNode.getValue()))));
        }
    }

    public <T> List<T> select(String path, Class<T> contentClass) {
        String query = String.format("* FROM [%s]", path);
        List<T> rows = new ArrayList<>();
        yt.tables().selectRows(query, YTableEntryTypes.yson(contentClass), (Consumer<T>) rows::add);
        return rows;
    }

    public <T> void insert(String path, Class<T> contentClass, List<T> content) {
        yt.tables().insertRows(simple(path), YTableEntryTypes.yson(contentClass), content);
    }

    public void deletePath(String path) {
        if (existsPath(path)) {
            yt.cypress().remove(simple(path));
        }
    }

    public boolean existsPath(String path) {
        return yt.cypress().exists(simple(path));
    }

    private static <T> ListF<MapF<String, String>> getSchemaFromClass(Class<T> contentClass) {
        return wrap(stream(contentClass.getDeclaredFields()).map(field -> {
            YTreeField yTreeField = field.getAnnotation(YTreeField.class);
            Column column = field.getAnnotation(Column.class);
            MapF<String, String> properties = map("name", yTreeField.key(), "type", column.type());
            if (isNotBlank(column.order())) {
                properties.put("sort_order", column.order());
            }
            return properties;
        }).collect(toList()));
    }

    private void waitMounted(YPath path) {
        waitInState(path, "mounted");
    }

    private void waitInState(YPath path, String state) {
        wait(() -> isInState(path, state));
    }

    private boolean isInState(YPath path, String state) {
        return yt.cypress().get(path.attribute("tablet_state")).stringValue().equals(state);
    }

    private void wait(Supplier<Boolean> condition) {
        await().atMost(TEN_SECONDS).pollInterval(TWO_HUNDRED_MILLISECONDS).until(() -> condition.get());
    }

}
