package ru.yandex.taxi.dmp.flink.connectors.yt.common;

import org.hamcrest.Matchers;
import org.junit.jupiter.api.Test;

import ru.yandex.taxi.dmp.flink.connectors.SerializationUtils;
import ru.yandex.yt.ytclient.tables.ColumnValueType;
import ru.yandex.yt.ytclient.tables.TableSchema;

import static org.hamcrest.MatcherAssert.assertThat;
import static org.junit.jupiter.api.Assertions.assertTrue;

class SerializableTableSchemaTest {
    @Test
    public void testSerializable() throws Exception {
        var schema = new TableSchema.Builder()
                .addKey("key", ColumnValueType.STRING)
                .addValue("value", ColumnValueType.INT64)
                .setUniqueKeys(true)
                .build();
        var serializableSchema = new SerializableTableSchema(schema);

        var bytes = SerializationUtils.serialize(serializableSchema);
        var result = (SerializableTableSchema) SerializationUtils.deserialize(bytes);

        assertTrue(result.toTableSchema().isUniqueKeys());
        assertThat(result.toTableSchema().getColumnNames(), Matchers.containsInAnyOrder("key", "value"));
    }
}
