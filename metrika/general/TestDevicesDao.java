package ru.yandex.metrika.mobmet.dao;

import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.List;
import java.util.Optional;

import org.jetbrains.annotations.Nullable;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Qualifier;

import ru.yandex.metrika.api.ObjectNotFoundException;
import ru.yandex.metrika.api.error.ConflictApiException;
import ru.yandex.metrika.dbclients.mysql.MySqlJdbcTemplate;
import ru.yandex.metrika.mobmet.model.TestDevice;
import ru.yandex.metrika.mobmet.model.TestDevicePurpose;
import ru.yandex.metrika.mobmet.model.TestDeviceType;

/**
 * Created by dlepex on 27.11.15.
 */
public class TestDevicesDao {

    private MySqlJdbcTemplate jdbc;

    @Qualifier("mobileTemplate")
    @Autowired
    public void setJdbc(MySqlJdbcTemplate jdbc) {
        this.jdbc = jdbc;
    }

    private static TestDevice rowMapper(ResultSet rs, int num) throws SQLException {
        final TestDevice device = new TestDevice();
        device.setId(rs.getLong("id"));
        device.setUid(rs.getLong("uid"));
        device.setName(rs.getString("name"));
        device.setDeviceId(rs.getString("device_id"));
        device.setPurpose(TestDevicePurpose.valueOf(rs.getString("purpose")));
        device.setType(TestDeviceType.valueOf(rs.getString("type")));
        device.setApplicationId(rs.getInt("app_id"));
        return device;
    }

    public @Nullable List<TestDevice> selectAll(int apiKey) {
        return jdbc.query("" +
                        "SELECT * " +
                        "FROM test_devices " +
                        "WHERE app_id=? " +
                        "   AND status='active'",
                TestDevicesDao::rowMapper,
                apiKey);
    }

    public @Nullable List<TestDevice> select(int api_key, TestDevicePurpose purpose) {
        return jdbc.query("" +
                        "SELECT * " +
                        "FROM test_devices " +
                        " WHERE app_id=? " +
                        "   AND status='active' " +
                        "   AND purpose=? ",
                TestDevicesDao::rowMapper,
                api_key,
                purpose.getDbName());
    }

    public Optional<TestDevice> selectSingle(int deviceId) {
        return jdbc.query("" +
                        "SELECT * " +
                        "FROM test_devices " +
                        "WHERE id=? " +
                        "   AND status='active'",
                TestDevicesDao::rowMapper,
                deviceId)
                .stream()
                .findFirst();
    }

    public @Nullable Long insert(TestDevice e) {
        return jdbc.updateRowGetGeneratedKeyNullable("" +
                        "INSERT INTO test_devices " +
                        "(uid, app_id, device_id, type, name, purpose) " +
                        "VALUES (?, ?, ?, ?, ?, ?) ",
                (ps) -> {
                    ps.setLong(1, e.getUid());
                    ps.setLong(2, e.getApplicationId());
                    ps.setString(3, e.getDeviceId());
                    ps.setString(4, e.getType().getDbName());
                    ps.setString(5, e.getName());
                    ps.setString(6, e.getPurpose().getDbName());
                });
    }

    public boolean update(TestDevice e) {
        return jdbc.update("" +
                        "UPDATE test_devices " +
                        "SET uid = ?, " +
                        "   device_id = ?, " +
                        "   type = ?, " +
                        "   name = ?,  " +
                        " purpose = ? " +
                        "WHERE id = ? " +
                        "   AND status='active'",
                e.getUid(),
                e.getDeviceId(),
                e.getType().getDbName(),
                e.getName(),
                e.getPurpose().getDbName(),
                e.getId()) > 0;

    }

    public boolean delete(long id) throws ObjectNotFoundException, ConflictApiException {
        return jdbc.update("" +
                        "UPDATE test_devices " +
                        "SET status='deleted' " +
                        "WHERE id=? " +
                        "   AND status='active'",
                id) != 0;
    }


}
