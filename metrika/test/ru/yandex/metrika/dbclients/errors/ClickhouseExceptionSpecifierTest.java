package ru.yandex.metrika.dbclients.errors;

import java.sql.SQLException;
import java.util.Arrays;
import java.util.Collection;

import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;

import ru.yandex.clickhouse.except.ClickHouseErrorCode;
import ru.yandex.metrika.dbclients.clickhouse.ClickhouseException;
import ru.yandex.metrika.dbclients.clickhouse.errors.ClickhouseApiException;
import ru.yandex.metrika.dbclients.clickhouse.errors.ClickhouseComplexQueryException;
import ru.yandex.metrika.dbclients.clickhouse.errors.ClickhouseDbException;
import ru.yandex.metrika.dbclients.clickhouse.errors.ClickhouseExceptionSpecifier;
import ru.yandex.metrika.dbclients.clickhouse.errors.ClickhouseQueryMemoryException;
import ru.yandex.metrika.dbclients.clickhouse.errors.ClickhouseQuerySizeException;
import ru.yandex.metrika.dbclients.clickhouse.errors.ClickhouseQueryTimeException;
import ru.yandex.metrika.dbclients.clickhouse.errors.ClickhouseUnhandledException;

import static org.junit.Assert.assertEquals;
import static ru.yandex.clickhouse.except.ClickHouseErrorCode.ATTEMPT_TO_READ_AFTER_EOF;
import static ru.yandex.clickhouse.except.ClickHouseErrorCode.CYCLIC_ALIASES;
import static ru.yandex.clickhouse.except.ClickHouseErrorCode.DISTRIBUTED_IN_JOIN_SUBQUERY_DENIED;
import static ru.yandex.clickhouse.except.ClickHouseErrorCode.EMPTY_QUERY;
import static ru.yandex.clickhouse.except.ClickHouseErrorCode.ILLEGAL_COLUMN;
import static ru.yandex.clickhouse.except.ClickHouseErrorCode.ILLEGAL_TYPE_OF_ARGUMENT;
import static ru.yandex.clickhouse.except.ClickHouseErrorCode.LOGICAL_ERROR;
import static ru.yandex.clickhouse.except.ClickHouseErrorCode.MEMORY_LIMIT_EXCEEDED;
import static ru.yandex.clickhouse.except.ClickHouseErrorCode.MULTIPLE_EXPRESSIONS_FOR_ALIAS;
import static ru.yandex.clickhouse.except.ClickHouseErrorCode.NETWORK_ERROR;
import static ru.yandex.clickhouse.except.ClickHouseErrorCode.NOT_FOUND_COLUMN_IN_BLOCK;
import static ru.yandex.clickhouse.except.ClickHouseErrorCode.NOT_IMPLEMENTED;
import static ru.yandex.clickhouse.except.ClickHouseErrorCode.OK;
import static ru.yandex.clickhouse.except.ClickHouseErrorCode.POCO_EXCEPTION;
import static ru.yandex.clickhouse.except.ClickHouseErrorCode.QUERY_WAS_CANCELLED;
import static ru.yandex.clickhouse.except.ClickHouseErrorCode.SET_SIZE_LIMIT_EXCEEDED;
import static ru.yandex.clickhouse.except.ClickHouseErrorCode.SOCKET_TIMEOUT;
import static ru.yandex.clickhouse.except.ClickHouseErrorCode.SYNTAX_ERROR;
import static ru.yandex.clickhouse.except.ClickHouseErrorCode.TABLE_ALREADY_EXISTS;
import static ru.yandex.clickhouse.except.ClickHouseErrorCode.TIMEOUT_EXCEEDED;
import static ru.yandex.clickhouse.except.ClickHouseErrorCode.TOO_BIG_AST;
import static ru.yandex.clickhouse.except.ClickHouseErrorCode.TOO_MUCH_BYTES;
import static ru.yandex.clickhouse.except.ClickHouseErrorCode.TOO_MUCH_PARTS;
import static ru.yandex.clickhouse.except.ClickHouseErrorCode.TOO_MUCH_ROWS;
import static ru.yandex.clickhouse.except.ClickHouseErrorCode.TOO_MUCH_TEMPORARY_NON_CONST_COLUMNS;
import static ru.yandex.clickhouse.except.ClickHouseErrorCode.TOO_SLOW;
import static ru.yandex.clickhouse.except.ClickHouseErrorCode.TYPE_MISMATCH;
import static ru.yandex.clickhouse.except.ClickHouseErrorCode.UNKNOWN_IDENTIFIER;
import static ru.yandex.clickhouse.except.ClickHouseErrorCode.UNKNOWN_TABLE;


@RunWith(Parameterized.class)
public class ClickhouseExceptionSpecifierTest {

    private static final Object[][] PARAMS = {
            {OK, ClickhouseUnhandledException.class}, // "SELECT 1"
            {NOT_FOUND_COLUMN_IN_BLOCK, ClickhouseApiException.class}, // "SELECT sum(a)"
            {ATTEMPT_TO_READ_AFTER_EOF, ClickhouseDbException.class},
            {ILLEGAL_TYPE_OF_ARGUMENT, ClickhouseApiException.class}, // "SELECT 1 + 'w6QTGgKeMyFtTj6'"
            {ILLEGAL_COLUMN, ClickhouseApiException.class}, //"SELECT materialize(1) AS `a`, materialize(`a`)", теперь OK
            {UNKNOWN_IDENTIFIER, ClickhouseApiException.class}, // "SELECT `a` + 1 as `a`"
            {NOT_IMPLEMENTED, ClickhouseApiException.class},
            {LOGICAL_ERROR, ClickhouseApiException.class},
            {TYPE_MISMATCH, ClickhouseApiException.class}, // "SELECT arrayJoin(1)"
            {TABLE_ALREADY_EXISTS, ClickhouseApiException.class},
            {UNKNOWN_TABLE, ClickhouseApiException.class}, // "SELECT materialize(1) FROM w6QTGgKeMyFtTj6"
            {SYNTAX_ERROR, ClickhouseApiException.class}, // "SELECT"}, теперь  UNKNOWN_IDENTIFIER на FORMAT
            {TOO_MUCH_ROWS, ClickhouseQuerySizeException.class},
            {TOO_MUCH_BYTES, ClickhouseQuerySizeException.class},
            {TIMEOUT_EXCEEDED, ClickhouseQueryTimeException.class},
            {TOO_SLOW, ClickhouseQueryTimeException.class},
            {TOO_MUCH_TEMPORARY_NON_CONST_COLUMNS, ClickhouseComplexQueryException.class},
            {TOO_BIG_AST, ClickhouseComplexQueryException.class},
            {CYCLIC_ALIASES, ClickhouseApiException.class}, // "SELECT ((((1 + d) as a) + 1) as b) + ((((1 + a) as c) + 1) as d)"
            {MULTIPLE_EXPRESSIONS_FOR_ALIAS, ClickhouseApiException.class}, // "SELECT 1 as `a`, 2 as `a`"
            {SET_SIZE_LIMIT_EXCEEDED, ClickhouseQueryMemoryException.class},
            {SOCKET_TIMEOUT, ClickhouseDbException.class},//"SELECT VisitID FROM visits_all"},
            {NETWORK_ERROR, ClickhouseDbException.class},
            {EMPTY_QUERY, ClickhouseApiException.class}, // no longer used
            {MEMORY_LIMIT_EXCEEDED, ClickhouseQueryMemoryException.class}, //"SELECT StartURL, count() FROM visits_all GROUP BY StartURL"},
            {TOO_MUCH_PARTS, ClickhouseDbException.class},
            {POCO_EXCEPTION, ClickhouseDbException.class},
            {QUERY_WAS_CANCELLED, ClickhouseDbException.class},
            {DISTRIBUTED_IN_JOIN_SUBQUERY_DENIED, ClickhouseApiException.class},
    };

    @Parameterized.Parameter
    public ClickHouseErrorCode errorCode;

    @Parameterized.Parameter(value = 1)
    public Class<?> expectedClass;

    @Parameterized.Parameters(name = "Error: {0}, expected exception: {1}")
    public static Collection<Object[]> data() {
        return Arrays.asList(PARAMS);
    }

    @Test
    public void checkException() {
        SQLException input = new SQLException("reason", "SQLState", errorCode.code);
        ClickhouseException actual = ClickhouseExceptionSpecifier.specify(input, "testHost", 8080);

        assertEquals(expectedClass, actual.getClass());
        assertEquals(errorCode.code, actual.getCode());
        assertEquals("testHost", actual.getHost());
        assertEquals(8080, actual.getPort());
    }
}
