package ru.yandex.metrika.dbclients.clickhouse.haze;

import org.springframework.jdbc.core.RowMapper;

import ru.yandex.metrika.util.Patterns;
import ru.yandex.metrika.util.chunk.ChunkDatabase;
import ru.yandex.metrika.util.chunk.ChunkDescriptor;
import ru.yandex.metrika.util.chunk.clickhouse.ChunkDatabaseCH;

/**
 * @author serebrserg
 * @since 22.06.16
 */
public class ChunkRowDescriptor implements ChunkDescriptor<ChunkRowForChecking> {

    private static final String FIELDS_UNSPLITTED = "IntVal,LongVal,StringVal";
    private static final String[] FIELDS = Patterns.COMMA.split(FIELDS_UNSPLITTED);

    @Override
    public String[] fields() {
        return FIELDS;
    }

    @Override
    public String fieldsUnsplitted()  {
        return FIELDS_UNSPLITTED;
    }

    @Override
    public String tableNamePrefix() {
        return "chunk_";
    }

    @Override
    public RowMapper<ChunkRowForChecking> rowMapper() {
        return (rs, rowNum) -> new ChunkRowForChecking(rs);
    }

    @Override
    public String createTableSql() {
        return "CREATE TABLE IF NOT EXISTS " + ChunkDatabase.TABLE_HOLDER + " (\n" +
                "    IntVal UInt32,\n" +
                "    LongVal UInt64,\n" +
                "    StringVal String\n" +
                " ) ENGINE = " + ChunkDatabaseCH.ENGINE_HOLDER;
    }

}
