package ru.yandex.metrika.tool;

import java.sql.SQLException;
import java.util.HashMap;
import java.util.Map;
import java.util.function.Predicate;

import com.mysql.cj.jdbc.MysqlConnectionPoolDataSource;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import ru.yandex.clickhouse.settings.ClickHouseProperties;
import ru.yandex.metrika.dbclients.clickhouse.ClickHouseSource;
import ru.yandex.metrika.dbclients.clickhouse.HttpTemplate;
import ru.yandex.metrika.dbclients.clickhouse.HttpTemplateImpl;
import ru.yandex.metrika.dbclients.clickhouse.MetrikaClickHouseProperties;
import ru.yandex.metrika.dbclients.mysql.MySqlJdbcTemplate;
import ru.yandex.metrika.util.chunk.ChunkDatabase;
import ru.yandex.metrika.util.chunk.clickhouse.ChunkDatabaseCH;

/**
 * @author orantius
 * @version $Id$
 * @since 7/4/11
 */
public class AllDatabases {

    private static final Logger log = LoggerFactory.getLogger(AllDatabases.class);

    /*  test dbs  */

    public static final CHChunkServer metrikadb02cCH = new CHChunkServer(
            getCHTemplate("localhost", 6308, "visit_log"),
            new Kind[]{Kind.hit,
                    Kind.visit,
                    Kind.user,
                    Kind.experiment,},
            new ChunkDatabase[]{
                    dbch("localhost", 6308, "hits", "WatchLog_Chunk_"),
                    dbch("localhost", 6308, "visit_log", "VisitCache_Chunk_"),
                    dbch("localhost", 6308, "user_history_log", "UserHistoryLog_"),
                    dbch("localhost", 6308, "wv_experiment", "_"),});

    public static final CHChunkServer mtcalus01t = new CHChunkServer(
            getCHTemplate("localhost", 6667, "visit_log"),
            new Kind[]{Kind.hit,
                    Kind.visit,
                    Kind.user,
                    Kind.experiment,},
            new ChunkDatabase[]{
                    dbch("localhost", 6667, "hits", "WatchLog_Chunk_"),
                    dbch("localhost", 6667, "visit_log", "VisitCache_Chunk_"),
                    dbch("localhost", 6667, "user_history_log", "UserHistoryLog_"),
                    dbch("localhost", 6667, "wv_experiment", "_"),});

    /*********mtcalc clichhouse ******/
    public static final CHChunkServer mtcalc07fCH = new CHChunkServer(
            getCHTemplate("localhost", 8273, "visit_log"),
            new Kind[]{Kind.hit,
                    Kind.visit,
                    Kind.user,
                    Kind.experiment,},
            new ChunkDatabase[]{
                    dbch("localhost", 8273, "hits", "WatchLog_Chunk_"),
                    dbch("localhost", 8273, "visit_log", "VisitCache_Chunk_"),
                    dbch("localhost", 8273, "user_history_log", "UserHistoryLog_"),
                    dbch("localhost", 8273, "wv_experiment", "_"),});

    public static final CHChunkServer mtcalc09CH = new CHChunkServer(
            getCHTemplate("localhost", 8293, "visit_log"),
            new Kind[]{Kind.hit,
                    Kind.visit,
                    Kind.user,
                    Kind.experiment,},
            new ChunkDatabase[]{
                    dbch("localhost", 8293, "hits", "WatchLog_Chunk_"),
                    dbch("localhost", 8293, "visit_log", "VisitCache_Chunk_"),
                    dbch("localhost", 8293, "user_history_log", "UserHistoryLog_"),
                    dbch("localhost", 8293, "wv_experiment", "_"),});

    /*********mtcalc clichhouse ******/
    public static final CHChunkServer mtcalc03cCH = new CHChunkServer(
            getCHTemplate("localhost", 8023, "visit_log"),
            new Kind[]{Kind.hit,
                    Kind.visit,
                    Kind.user,
                    Kind.experiment,},
            new ChunkDatabase[]{
                    dbch("localhost", 8023, "hits", "WatchLog_Chunk_"),
                    dbch("localhost", 8023, "visit_log", "VisitCache_Chunk_"),
                    dbch("localhost", 8023, "user_history_log", "UserHistoryLog_"),
                    dbch("localhost", 8023, "wv_experiment", "_"),});

    public static final CHChunkServer mtcalc02cCH = new CHChunkServer(
            getCHTemplate("localhost", 8013, "visit_log"),
            new Kind[]{Kind.hit,
                    Kind.visit,
                    Kind.user,
                    Kind.experiment,},
            new ChunkDatabase[]{
                    dbch("localhost", 8013, "hits", "WatchLog_Chunk_"),
                    dbch("localhost", 8013, "visit_log", "VisitCache_Chunk_"),
                    dbch("localhost", 8013, "user_history_log", "UserHistoryLog_"),
                    dbch("localhost", 8013, "wv_experiment", "_"),});

    /***************/

    static final class Long128 {
        long l;
        long l2;

        @Override
        public boolean equals(Object o) {
            if (this == o) {
                return true;
            }
            if (o == null || getClass() != o.getClass()) {
                return false;
            }

            Long128 long128 = (Long128) o;

            if (l != long128.l) {
                return false;
            }
            return l2 == long128.l2;
        }

        @Override
        public int hashCode() {
            int result = (int) (l ^ (l >>> 32));
            result = 31 * result + (int) (l2 ^ (l2 >>> 32));
            return result;
        }

        Long128(long l, long l2) {
            this.l = l;
            this.l2 = l2;
        }

        @Override
        public String toString() {
            return "{c=" + (l / (1L << 31)) + " h=" + (l % (1L << 31)) + ",u=" + l2 + '}';
        }
    }

    private static ChunkDatabaseCH dbch(String host, int port, String dbName, String tablePrefix) {
        ChunkDatabaseCH res = new ChunkDatabaseCH();
        res.setHttpTemplate(getCHTemplate(host, port, dbName));
        res.setTablePrefix(tablePrefix);
        return res;
    }

    public static Predicate<String> all() {
        return s -> true;
    }

    public static Predicate<String> before(final String arg) {
        return s -> s.compareTo(arg) <= 0;
    }

    public static Predicate<String> after(final String arg) {
        return s -> s.compareTo(arg) >= 0;
    }

    public static Predicate<String> between(final String left, final String right) {
        return s -> s.compareTo(left) >= 0 && s.compareTo(right) <= 0;
    }

    public static Predicate<String> startWith(final String prefix) {
        return s -> s.startsWith(prefix);
    }

    enum Kind {
        hit, visit, user, eeevent, eeevent_f, page, error, experiment
    }

    public static class AbstractChunkServer {
        Map<Kind, ChunkDatabase> databases = new HashMap<>();

    }

    public static class CHChunkServer extends AbstractChunkServer{
        HttpTemplate template;

        CHChunkServer(HttpTemplate template, Kind[] kinds, ChunkDatabase[] databases) {
            this.template = template;
            for (int i = 0; i < kinds.length; i++) {
                ChunkDatabaseCH di = (ChunkDatabaseCH) databases[i];
                try {
                    di.afterPropertiesSet();
                } catch (Exception e) {
                    e.printStackTrace();  //To change body of catch statement use File | Settings | File Templates.
                }
                this.databases.put(kinds[i], di);
            }
        }

        public HttpTemplate getTemplate() {
            return template;
        }
    }

    public static MySqlJdbcTemplate getTemplate(String serverName, int port, String user, String password, String db) {
        try {
            MysqlConnectionPoolDataSource ds = getDataSource(serverName, port, user, password, db);
            //ds.setProfileSQL(true);
            return new MySqlJdbcTemplate(ds);
        } catch (Exception e) {
            e.printStackTrace();
            return null;
        }
    }

    public static MysqlConnectionPoolDataSource getDataSource(String serverName, int port, String user, String password, String db) throws SQLException {
        MysqlConnectionPoolDataSource ds = new MysqlConnectionPoolDataSource();
        ds.setPort(port);
        ds.setServerName(serverName);
        ds.setUser(user);
        ds.setPassword(password);
        ds.setDatabaseName(db);
        ds.setAllowMultiQueries(true);
        ds.setZeroDateTimeBehavior("CONVERT_TO_NULL");
        ds.setRewriteBatchedStatements(false);
        ds.setLogger("Slf4JLogger");
        ds.setDontTrackOpenResources(true);
        ds.setUseServerPrepStmts(false);
        ds.setDumpQueriesOnException(true);
        ds.setElideSetAutoCommits(true);
        ds.setUseLocalSessionState(true);
        ds.setAlwaysSendSetIsolation(false);
        ds.setCacheServerConfiguration(true);
        //ds.setSessionVariables("low_priority_updates=1"); // commented: -1 query,
        ds.setCharacterSetResults("utf8"); // uncommented: -1 query
        ds.setJdbcCompliantTruncation(false); // uncommented: -1 query
        ds.setNoDatetimeStringSync(true);
        return ds;
    }

    public static HttpTemplateImpl getCHTemplate(String serverName, int port, String db) {
        return getCHTemplate(serverName, port, db, new MetrikaClickHouseProperties());
    }

    public static HttpTemplateImpl getCHTemplate(String serverName, int port, String db, ClickHouseProperties properties) {
        try {
            ClickHouseSource clickHouseSource = new ClickHouseSource(serverName, port, db);
            HttpTemplateImpl template = new HttpTemplateImpl(clickHouseSource, properties);
            template.afterPropertiesSet();
            return template;
        } catch (Exception e) {
            e.printStackTrace();
            return null;
        }
    }

}
