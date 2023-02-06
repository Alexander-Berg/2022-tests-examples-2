package ru.yandex.metrika.util.chunk.clickhouse;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

import com.codahale.metrics.MetricRegistry;
import com.google.common.collect.Lists;
import org.apache.logging.log4j.Level;
import org.jetbrains.annotations.NotNull;
import org.junit.Ignore;
import org.junit.Test;

import ru.yandex.metrika.dbclients.clickhouse.HttpTemplate;
import ru.yandex.metrika.tool.AllDatabases;
import ru.yandex.metrika.util.chunk.ChunkDatabase;
import ru.yandex.metrika.util.chunk.ChunkDescriptor;
import ru.yandex.metrika.util.chunk.ChunkRow;
import ru.yandex.metrika.util.chunk.output.CommandOutput;
import ru.yandex.metrika.util.log.Log4jSetup;

import static org.junit.Assert.assertEquals;

/**
 *  ssh -L 8123:localhost:8123 mtweb02t
 * OMG да это же первый тест, юзающий реальный кликхаус и не стоящий в игноре!
 * @author jkee
 */
@Ignore("METRIQA-936")
public class ChunkBuilderCHTest {
    private static class TestEntity implements ChunkRow {

        public static final String COLUMNS = "id,someString, someBlob";
        private static final ChunkDescriptor INSERT = ChunkRow.fromCol(COLUMNS);

        private long id;
        private String someString;
        private byte[] someBlob;

        private TestEntity(long id, String someString) {
            this.id = id;
            this.someString = someString;
            this.someBlob = someString.getBytes();
        }

        @Override
        public long getTime() {
            throw new UnsupportedOperationException();
        }

        @Override
        public ChunkDescriptor getInsertDescr() {
            return INSERT;
        }

        @Override
        public void dumpFields(@NotNull CommandOutput output) {
            output.outNotNull(id);
            output.out(someString);
            output.out(someBlob);
        }

        @Override
        public boolean equals(Object o) {
            if (this == o) return true;
            if (!(o instanceof TestEntity)) return false;

            TestEntity that = (TestEntity) o;

            if (id != that.id) return false;
            if (!Arrays.equals(someBlob, that.someBlob)) return false;
            if (someString != null ? !someString.equals(that.someString) : that.someString != null) return false;

            return true;
        }

        @Override
        public int hashCode() {
            int result = (int) (id ^ (id >>> 32));
            result = 31 * result + (someString != null ? someString.hashCode() : 0);
            result = 31 * result + (someBlob != null ? Arrays.hashCode(someBlob) : 0);
            return result;
        }

        @Override
        public String toString() {
            return "TestEntity{" +
                    "id=" + id +
                    ", someString='" + someString + '\'' +
                    '}';
        }
    }

    @Test
    public void testCreateChunk() throws Exception {
        Log4jSetup.basicSetup(Level.INFO);
        ChunkDatabaseCH chunkDatabaseCH = new ChunkDatabaseCH();
        chunkDatabaseCH.setMetricRegistry(new MetricRegistry());
        HttpTemplate chTemplate = AllDatabases.getCHTemplate("localhost", 8123, "test");
        chTemplate.update("DROP TABLE IF EXISTS Test_201307030842011011030");
        chTemplate.update("DROP TABLE IF EXISTS A_tmp_table_201307030842011011030");
        chunkDatabaseCH.setHttpTemplate(chTemplate);
        chunkDatabaseCH.setTablePrefix("Test_");
        chunkDatabaseCH.setWriteEnabled(true);
        chunkDatabaseCH.afterPropertiesSet();

        List<TestEntity> entities = new ArrayList<>();
        TestEntity te1 = new TestEntity(100, "xzcxhfajlf24131");
        entities.add(te1);
        TestEntity te2 = new TestEntity(101, "\r\n\b\t\'\'");
        entities.add(te2);
        TestEntity te3 = new TestEntity(9223372036854775807L, "\r\n\b\'\'");
        entities.add(te3);

        ChunkBuilderCH<TestEntity> cb = new ChunkBuilderCH<TestEntity>("201307030842011011030", chunkDatabaseCH) {
            @Override
            protected String getCreateTable() {
                return "CREATE TABLE " + ChunkDatabase.TABLE_HOLDER + '(' +
                        "     id UInt64," +
                        "    someString String," +
                        "    someBlob String" +
                        ") ENGINE = StripeLog";
            }

            @Override
            protected String getColumns() {
                return TestEntity.COLUMNS;
            }
        };
        for (TestEntity entity : entities) {
            cb.addRow(entity);
        }

        cb.flush();

        List<TestEntity> query = chTemplate.query("SELECT * from Test_201307030842011011030", (rs, rowNum) -> {
            TestEntity testEntity = new TestEntity(rs.getLong(1), rs.getString(2));
            testEntity.someBlob = rs.getBytes(3);
            return testEntity;
        });


        chTemplate.update("DROP TABLE Test_201307030842011011030");

        assertEquals(Lists.newArrayList(te1, te2, te3), query);


    }
}
