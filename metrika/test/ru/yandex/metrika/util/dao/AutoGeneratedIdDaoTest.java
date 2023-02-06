package ru.yandex.metrika.util.dao;

import java.util.Objects;

import com.google.common.collect.ImmutableMap;
import org.junit.Test;
import org.mockito.hamcrest.MockitoHamcrest;
import org.springframework.jdbc.core.namedparam.SqlParameterSource;
import org.springframework.jdbc.support.KeyHolder;

import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.hasProperty;
import static org.junit.Assert.assertEquals;
import static org.mockito.Matchers.any;
import static org.mockito.Matchers.anyString;
import static org.mockito.Matchers.eq;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

public class AutoGeneratedIdDaoTest extends GenericJdbcDaoTestBase<AutoGeneratedIdDaoTest.AutoGeneratedIdEntity> {

    public AutoGeneratedIdDaoTest() {
        super(AutoGeneratedIdEntity.class);
    }

    @Override
    protected AutoGeneratedIdEntity createEntityInstance() {
        AutoGeneratedIdEntity entityInstance = new AutoGeneratedIdEntity();
        entityInstance.setId(1);
        entityInstance.setName("Name");
        return entityInstance;
    }

    @Override
    protected GenericJdbcDao<AutoGeneratedIdEntity> createDao() {
        GenericJdbcDao<AutoGeneratedIdEntity> result = super.createDao();
        when(result.getJdbcTemplate().update(anyString(), any(SqlParameterSource.class), any(KeyHolder.class))).then(invocation -> {
            invocation.getArgument(2, KeyHolder.class).getKeyList().add(ImmutableMap.of("key", 1));
            return 1;
        });
        return result;
    }

    @Test
    public void testCreate() {
        dao.create(entityInstance);

        verify(dao.getJdbcTemplate()).update(
                eq("INSERT INTO `auto_generated_id_entity` (`name`) VALUES (:name)"),
                MockitoHamcrest.argThat(hasProperty("values", equalTo(ImmutableMap.of("name", "Name")))),
                any(KeyHolder.class)
        );

        assertEquals(1, entityInstance.getId());
    }

    @Table(value = AutoGeneratedIdEntity.TABLE_NAME, autoGeneratedId = true)
    public static class AutoGeneratedIdEntity {

        public static final String TABLE_NAME = "auto_generated_id_entity";

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
            AutoGeneratedIdEntity that = (AutoGeneratedIdEntity) o;
            return id == that.id &&
                    Objects.equals(name, that.name);
        }

        @Override
        public int hashCode() {
            return Objects.hash(id, name);
        }
    }
}