package ru.yandex.metrika.util.dao;

import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;

import com.google.common.collect.ImmutableList;
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

public class BasicDaoTest extends GenericJdbcDaoTestBase<BasicDaoTest.BasicEntity> {

    public BasicDaoTest() {
        super(BasicEntity.class);
    }

    @Override
    protected BasicEntity createEntityInstance() {
        BasicEntity entityInstance = new BasicEntity();
        entityInstance.setId(1);
        entityInstance.setName("Name");
        return entityInstance;
    }

    @Test
    public void testCreate() {
        dao.create(entityInstance);

        verify(dao.getJdbcTemplate()).update(
                eq("INSERT INTO `basic_entity` (`id`, `name`) VALUES (:id, :name)"),
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
                eq("UPDATE `basic_entity` AS `t` SET `t`.`name` = :name WHERE `t`.`id` = :id"),
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
                eq("UPDATE `basic_entity` AS `t` SET `t`.`name` = :name WHERE `t`.`id` = :id"),
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
                eq("DELETE `t` FROM `basic_entity` AS `t` WHERE `t`.`id` = :id"),
                eq(ImmutableMap.of("id", 1))
        );
    }

    @Test
    public void testDeleteById() {
        dao.deleteById(1);

        verify(dao.getJdbcTemplate()).update(
                eq("DELETE `t` FROM `basic_entity` AS `t` WHERE `t`.`id` = :id"),
                eq(ImmutableMap.of("id", 1))
        );
    }

    @Test
    public void testDeleteByIdMap() {
        dao.deleteById(ImmutableMap.of("id", 1));

        verify(dao.getJdbcTemplate()).update(
                eq("DELETE `t` FROM `basic_entity` AS `t` WHERE `t`.`id` = :id"),
                eq(ImmutableMap.of("id", 1))
        );
    }

    @Test
    public void testDeleteByCondition() {
        dao.deleteByCondition("WHERE id = ?", 1);

        verify(dao.getJdbcTemplate().getJdbcOperations()).update(
                eq("DELETE `t` FROM `basic_entity` AS `t` WHERE id = ?"),
                eq(1)
        );
    }

    @Test
    public void testDeleteByConditionMap() {
        dao.deleteByCondition("WHERE id = :id", ImmutableMap.of("id", 1));

        verify(dao.getJdbcTemplate()).update(
                eq("DELETE `t` FROM `basic_entity` AS `t` WHERE id = :id"),
                eq(ImmutableMap.of("id", 1))
        );
    }

    @Test
    public void testGetById() {
        BasicEntity result = dao.getById(1);

        verify(dao.getJdbcTemplate()).query(
                eq("SELECT `t`.`id`, `t`.`name` FROM `basic_entity` AS `t` WHERE `t`.`id` = :id"),
                eq(ImmutableMap.of("id", 1)),
                Matchers.<RowMapper<Object>>any()
        );

        assertEquals(entityInstance, result);
    }

    @Test
    public void testGetByIdMap() {
        BasicEntity result = dao.getById(ImmutableMap.of("id", 1));

        verify(dao.getJdbcTemplate()).query(
                eq("SELECT `t`.`id`, `t`.`name` FROM `basic_entity` AS `t` WHERE `t`.`id` = :id"),
                eq(ImmutableMap.of("id", 1)),
                Matchers.<RowMapper<Object>>any()
        );

        assertEquals(entityInstance, result);
    }

    @Test
    public void testGetByCondition() {
        BasicEntity result = dao.getByCondition("WHERE id = ?", 1);

        verify(dao.getJdbcTemplate().getJdbcOperations()).query(
                eq("SELECT `t`.`id`, `t`.`name` FROM `basic_entity` AS `t` WHERE id = ?"),
                Matchers.<RowMapper<Object>>any(),
                eq(1)
        );

        assertEquals(entityInstance, result);
    }

    @Test
    public void testGetByConditionMap() {
        BasicEntity result = dao.getByCondition("WHERE id = :id", ImmutableMap.of("id", 1));

        verify(dao.getJdbcTemplate()).query(
                eq("SELECT `t`.`id`, `t`.`name` FROM `basic_entity` AS `t` WHERE id = :id"),
                eq(ImmutableMap.of("id", 1)),
                Matchers.<RowMapper<Object>>any()
        );

        assertEquals(entityInstance, result);
    }

    @Test
    public void testGetByQuery() {
        BasicEntity result = dao.getByQuery("SELECT * from basic_entity WHERE id = ?", 1);

        verify(dao.getJdbcTemplate().getJdbcOperations()).query(
                eq("SELECT * from basic_entity WHERE id = ?"),
                Matchers.<RowMapper<Object>>any(),
                eq(1)
        );

        assertEquals(entityInstance, result);
    }

    @Test
    public void testGetByQueryMap() {
        BasicEntity result = dao.getByQuery("SELECT * from basic_entity WHERE id = :id", ImmutableMap.of("id", 1));

        verify(dao.getJdbcTemplate()).query(
                eq("SELECT * from basic_entity WHERE id = :id"),
                eq(ImmutableMap.of("id", 1)),
                Matchers.<RowMapper<Object>>any()
        );

        assertEquals(entityInstance, result);
    }

    @Test
    public void testFindById() {
        Optional<BasicEntity> result = dao.findById(1);

        verify(dao.getJdbcTemplate()).query(
                eq("SELECT `t`.`id`, `t`.`name` FROM `basic_entity` AS `t` WHERE `t`.`id` = :id"),
                eq(ImmutableMap.of("id", 1)),
                Matchers.<RowMapper<Object>>any()
        );

        assertEquals(Optional.of(entityInstance), result);
    }

    @Test
    public void testFindByIdMap() {
        Optional<BasicEntity> result = dao.findById(ImmutableMap.of("id", 1));

        verify(dao.getJdbcTemplate()).query(
                eq("SELECT `t`.`id`, `t`.`name` FROM `basic_entity` AS `t` WHERE `t`.`id` = :id"),
                eq(ImmutableMap.of("id", 1)),
                Matchers.<RowMapper<Object>>any()
        );

        assertEquals(Optional.of(entityInstance), result);
    }

    @Test
    public void testFindByCondition() {
        Optional<BasicEntity> result = dao.findByCondition("WHERE id = ?", 1);

        verify(dao.getJdbcTemplate().getJdbcOperations()).query(
                eq("SELECT `t`.`id`, `t`.`name` FROM `basic_entity` AS `t` WHERE id = ?"),
                Matchers.<RowMapper<Object>>any(),
                eq(1)
        );

        assertEquals(Optional.of(entityInstance), result);
    }

    @Test
    public void testFindByConditionMap() {
        Optional<BasicEntity> result = dao.findByCondition("WHERE id = :id", ImmutableMap.of("id", 1));

        verify(dao.getJdbcTemplate()).query(
                eq("SELECT `t`.`id`, `t`.`name` FROM `basic_entity` AS `t` WHERE id = :id"),
                eq(ImmutableMap.of("id", 1)),
                Matchers.<RowMapper<Object>>any()
        );

        assertEquals(Optional.of(entityInstance), result);
    }

    @Test
    public void testFindByQuery() {
        Optional<BasicEntity> result = dao.findByQuery("SELECT * from basic_entity WHERE id = ?", 1);

        verify(dao.getJdbcTemplate().getJdbcOperations()).query(
                eq("SELECT * from basic_entity WHERE id = ?"),
                Matchers.<RowMapper<Object>>any(),
                eq(1)
        );

        assertEquals(Optional.of(entityInstance), result);
    }

    @Test
    public void testFindByQueryMap() {
        Optional<BasicEntity> result = dao.findByQuery("SELECT * from basic_entity WHERE id = :id", ImmutableMap.of("id", 1));

        verify(dao.getJdbcTemplate()).query(
                eq("SELECT * from basic_entity WHERE id = :id"),
                eq(ImmutableMap.of("id", 1)),
                Matchers.<RowMapper<Object>>any()
        );

        assertEquals(Optional.of(entityInstance), result);
    }

    @Test
    public void testFindAll() {
        List<BasicEntity> result = dao.findAll();

        verify(dao.getJdbcTemplate()).query(
                eq("SELECT `t`.`id`, `t`.`name` FROM `basic_entity` AS `t`"),
                eq(ImmutableMap.of()),
                Matchers.<RowMapper<Object>>any()
        );

        assertEquals(ImmutableList.of(entityInstance), result);
    }

    @Test
    public void testFindAllByCondition() {
        List<BasicEntity> result = dao.findAllByCondition("WHERE name = ?", "Name");

        verify(dao.getJdbcTemplate().getJdbcOperations()).query(
                eq("SELECT `t`.`id`, `t`.`name` FROM `basic_entity` AS `t` WHERE name = ?"),
                Matchers.<RowMapper<Object>>any(),
                eq("Name")
        );

        assertEquals(ImmutableList.of(entityInstance), result);
    }

    @Test
    public void testFindAllByConditionMap() {
        List<BasicEntity> result = dao.findAllByCondition("WHERE name = :name", ImmutableMap.of("name", "Name"));

        verify(dao.getJdbcTemplate()).query(
                eq("SELECT `t`.`id`, `t`.`name` FROM `basic_entity` AS `t` WHERE name = :name"),
                eq(ImmutableMap.of("name", "Name")),
                Matchers.<RowMapper<Object>>any()
        );

        assertEquals(ImmutableList.of(entityInstance), result);
    }

    @Test
    public void testFindAllByQuery() {
        List<BasicEntity> result = dao.findAllByQuery("SELECT * FROM basic_entity WHERE name = ?", "Name");

        verify(dao.getJdbcTemplate().getJdbcOperations()).query(
                eq("SELECT * FROM basic_entity WHERE name = ?"),
                Matchers.<RowMapper<Object>>any(),
                eq("Name")
        );

        assertEquals(ImmutableList.of(entityInstance), result);
    }

    @Test
    public void testFindAllByQueryMap() {
        List<BasicEntity> result = dao.findAllByQuery("SELECT * FROM basic_entity WHERE name = :name", ImmutableMap.of("name", "Name"));

        verify(dao.getJdbcTemplate()).query(
                eq("SELECT * FROM basic_entity WHERE name = :name"),
                eq(ImmutableMap.of("name", "Name")),
                Matchers.<RowMapper<Object>>any()
        );

        assertEquals(ImmutableList.of(entityInstance), result);
    }

    @Test
    public void testCount() {
        long result = dao.count();

        verify(dao.getJdbcTemplate()).queryForObject(
                eq("SELECT COUNT(*) FROM `basic_entity` AS `t`"),
                eq(ImmutableMap.of()),
                Matchers.<RowMapper<Long>>any()
        );

        assertEquals(1L, result);
    }

    @Test
    public void testCountByCondition() {
        long result = dao.countByCondition("WHERE name = ?", "Name");

        verify(dao.getJdbcTemplate().getJdbcOperations()).queryForObject(
                eq("SELECT COUNT(*) FROM `basic_entity` AS `t` WHERE name = ?"),
                Matchers.<RowMapper<Long>>any(),
                eq("Name")
        );

        assertEquals(1L, result);
    }

    @Test
    public void testCountByConditionMap() {
        long result = dao.countByCondition("WHERE name = :name", ImmutableMap.of("name", "Name"));

        verify(dao.getJdbcTemplate()).queryForObject(
                eq("SELECT COUNT(*) FROM `basic_entity` AS `t` WHERE name = :name"),
                eq(ImmutableMap.of("name", "Name")),
                Matchers.<RowMapper<Long>>any()
        );

        assertEquals(1L, result);
    }

    @Test
    public void testCountByQuery() {
        long result = dao.countByQuery("SELECT COUNT(*) FROM basic_entity WHERE name = ?", "Name");

        verify(dao.getJdbcTemplate().getJdbcOperations()).queryForObject(
                eq("SELECT COUNT(*) FROM basic_entity WHERE name = ?"),
                Matchers.<RowMapper<Long>>any(),
                eq("Name")
        );

        assertEquals(1L, result);
    }

    @Test
    public void testCountByQueryMap() {
        long result = dao.countByQuery("SELECT COUNT(*) FROM basic_entity WHERE name = :name", ImmutableMap.of("name", "Name"));

        verify(dao.getJdbcTemplate()).queryForObject(
                eq("SELECT COUNT(*) FROM basic_entity WHERE name = :name"),
                eq(ImmutableMap.of("name", "Name")),
                Matchers.<RowMapper<Long>>any()
        );

        assertEquals(1L, result);
    }

    @Table(BasicEntity.TABLE_NAME)
    public static class BasicEntity {

        public static final String TABLE_NAME = "basic_entity";

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
            BasicEntity that = (BasicEntity) o;
            return id == that.id &&
                    Objects.equals(name, that.name);
        }

        @Override
        public int hashCode() {
            return Objects.hash(id, name);
        }
    }
}
