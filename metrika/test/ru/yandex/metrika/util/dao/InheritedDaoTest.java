package ru.yandex.metrika.util.dao;

import java.util.Map;
import java.util.Objects;

import com.google.common.collect.ImmutableMap;
import org.junit.Test;
import org.mockito.Matchers;
import org.mockito.hamcrest.MockitoHamcrest;
import org.springframework.jdbc.core.RowMapper;
import org.springframework.jdbc.core.namedparam.SqlParameterSource;
import org.springframework.jdbc.support.KeyHolder;

import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.hasProperty;
import static org.junit.Assert.assertEquals;
import static org.mockito.Matchers.any;
import static org.mockito.Matchers.eq;
import static org.mockito.Mockito.verify;

public class InheritedDaoTest extends GenericJdbcDaoTestBase<InheritedDaoTest.InheritedEntity> {

    public InheritedDaoTest() {
        super(InheritedEntity.class);
    }

    @Override
    protected InheritedEntity createEntityInstance() {
        InheritedEntity entityInstance = new InheritedEntity();
        entityInstance.setId(1);
        entityInstance.setName("Name");
        return entityInstance;
    }

    @Test
    public void testCreate() {
        dao.create(entityInstance);

        verify(dao.getJdbcTemplate()).update(
                eq("INSERT INTO `inherited_entity` (`id`, `name`) VALUES (:id, :name)"),
                MockitoHamcrest.argThat(hasProperty("values", equalTo(ImmutableMap.builder()
                        .put("id", 1)
                        .put("name", "Name")
                        .build()
                ))),
                any(KeyHolder.class)
        );
    }

    @Test
    public void testUpdate() {
        dao.update(entityInstance);

        verify(dao.getJdbcTemplate()).update(
                eq("UPDATE `inherited_entity` AS `t` SET `t`.`name` = :name WHERE `t`.`id` = :id"),
                MockitoHamcrest.<SqlParameterSource>argThat(hasProperty("values", equalTo(ImmutableMap.<String, Object>builder()
                        .put("id", 1)
                        .put("name", "Name")
                        .build()
                )))
        );
    }

    @Test
    public void testUpdateMap() {
        dao.update(Map.of("name", "Name"), 1);

        verify(dao.getJdbcTemplate()).update(
                eq("UPDATE `inherited_entity` AS `t` SET `t`.`name` = :name WHERE `t`.`id` = :id"),
                MockitoHamcrest.<SqlParameterSource>argThat(hasProperty("values", equalTo(ImmutableMap.<String, Object>builder()
                        .put("id", 1)
                        .put("name", "Name")
                        .build()
                )))
        );
    }

    @Test
    public void testDelete() {
        dao.delete(entityInstance);

        verify(dao.getJdbcTemplate()).update(
                eq("DELETE `t` FROM `inherited_entity` AS `t` WHERE `t`.`id` = :id"),
                eq(ImmutableMap.of("id", 1))
        );
    }

    @Test
    public void testGetById() {
        InheritedEntity result = dao.getById(1);

        verify(dao.getJdbcTemplate()).query(
                eq("SELECT `t`.`id`, `t`.`name` FROM `inherited_entity` AS `t` WHERE `t`.`id` = :id"),
                eq(ImmutableMap.of("id", 1)),
                Matchers.<RowMapper<Object>>any()
        );

        assertEquals(entityInstance, result);
    }

    @Table(InheritedEntity.TABLE_NAME)
    public static class InheritedEntity extends InheritedEntityBase {

        public static final String TABLE_NAME = "inherited_entity";

        private String name;

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
            if (!super.equals(o)) return false;
            InheritedEntity that = (InheritedEntity) o;
            return Objects.equals(name, that.name);
        }

        @Override
        public int hashCode() {
            return Objects.hash(super.hashCode(), name);
        }
    }

    public static class InheritedEntityBase {

        @Id
        private int id;

        public int getId() {
            return id;
        }

        public void setId(int id) {
            this.id = id;
        }

        @Override
        public boolean equals(Object o) {
            if (this == o) return true;
            if (o == null || getClass() != o.getClass()) return false;
            InheritedEntityBase that = (InheritedEntityBase) o;
            return id == that.id;
        }

        @Override
        public int hashCode() {
            return Objects.hash(id);
        }
    }
}
