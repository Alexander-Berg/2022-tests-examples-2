package ru.yandex.metrika.util.dao;

import java.sql.ResultSet;
import java.sql.ResultSetMetaData;
import java.sql.SQLException;
import java.util.Objects;

import org.junit.Assert;
import org.junit.Before;
import org.junit.Test;

import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

public class MetadataBasedRowMapperTest {

    private MetadataBasedRowMapper<Entity> rowMapper;
    private Entity entityInstance;
    private ResultSet resultSet;

    @Before
    public void init() throws SQLException {
        JdbcMetadataGenerator jdbcMetadataGenerator = new JdbcMetadataGenerator();
        rowMapper = new MetadataBasedRowMapper<>(jdbcMetadataGenerator.generateMeta(Entity.class));

        entityInstance = new Entity();
        entityInstance.setId(1);
        entityInstance.setName("Name");

        ResultSetMetaData resultSetMetaData = mock(ResultSetMetaData.class);
        when(resultSetMetaData.getColumnCount()).thenReturn(2);
        when(resultSetMetaData.getColumnName(1)).thenReturn("id");
        when(resultSetMetaData.getColumnName(2)).thenReturn("name");

        resultSet = mock(ResultSet.class);
        when(resultSet.getMetaData()).thenReturn(resultSetMetaData);
        when(resultSet.getInt(1)).thenReturn(1);
        when(resultSet.getString(2)).thenReturn("Name");
    }

    @Test
    public void test() throws SQLException {
        Entity result = rowMapper.mapRow(resultSet, 0);

        Assert.assertEquals(result, entityInstance);
    }

    @Table(Entity.TABLE_NAME)
    public static class Entity {

        public static final String TABLE_NAME = "entity";

        @Id
        private int id;

        private String name;

        public int getId() {
            return id;
        }

        public void setId(int id) {
            this.id = id;
        }

        public String getName() {
            return name;
        }

        public void setName(String name) {
            this.name = name;
        }

        @Override
        public boolean equals(Object o) {
            if (this == o) return true;
            if (o == null || getClass() != o.getClass()) return false;
            Entity entity = (Entity) o;
            return id == entity.id &&
                    Objects.equals(name, entity.name);
        }

        @Override
        public int hashCode() {
            return Objects.hash(id, name);
        }
    }
}
