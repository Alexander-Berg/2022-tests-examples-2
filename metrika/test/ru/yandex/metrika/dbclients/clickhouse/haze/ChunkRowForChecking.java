package ru.yandex.metrika.dbclients.clickhouse.haze;

import java.sql.ResultSet;
import java.sql.SQLException;

import org.jetbrains.annotations.NotNull;

import ru.yandex.metrika.util.chunk.ChunkDescriptor;
import ru.yandex.metrika.util.chunk.ChunkRow;
import ru.yandex.metrika.util.chunk.output.CommandOutput;

/**
 * @author serebrserg
 * @since 12.02.16
 */
public class ChunkRowForChecking implements ChunkRow {
    public static final String COLUMNS = "IntVal, LongVal, StringVal";

    public static final ChunkDescriptor INSERT = ChunkRow.fromCol(COLUMNS);

    private final int intVal;
    private final long longVal;
    private final String stringVal;

    @Override
    public long getTime() {
        return 0;
    }

    @Override
    public ChunkDescriptor getInsertDescr() {
        return INSERT;
    }

    @Override
    public void dumpFields(@NotNull CommandOutput output) {
        output.outNotNull(intVal)
                .outNotNull(longVal)
                .out(stringVal);
    }

    public ChunkRowForChecking(int intVal, long longVal, String stringVal) {
        this.intVal = intVal;
        this.longVal = longVal;
        this.stringVal = stringVal;
    }

    public ChunkRowForChecking(ResultSet resultSet) throws SQLException {
        intVal = Integer.parseUnsignedInt(resultSet.getString("IntVal"));
        longVal = Integer.parseUnsignedInt(resultSet.getString("LongVal"));
        stringVal = resultSet.getString("StringVal");
    }

    @Override
    public String toString() {
        return "TestChunkRow{" +
                "intVal=" + intVal +
                ", longVal=" + longVal +
                ", stringVal='" + stringVal + '\'' +
                '}';
    }
}
