package ru.yandex.metrika.util.dao;

import java.util.List;
import java.util.Optional;

import com.google.common.collect.ImmutableList;
import com.google.common.collect.ImmutableMap;
import org.junit.Test;
import org.mockito.Matchers;
import org.springframework.dao.EmptyResultDataAccessException;
import org.springframework.jdbc.core.RowMapper;

import static org.junit.Assert.assertEquals;
import static org.mockito.Matchers.any;
import static org.mockito.Matchers.anyMapOf;
import static org.mockito.Matchers.anyString;
import static org.mockito.Matchers.eq;
import static org.mockito.Matchers.startsWith;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

public class BasicDaoNegativeTest extends GenericJdbcDaoTestBase<BasicDaoTest.BasicEntity> {

    public BasicDaoNegativeTest() {
        super(BasicDaoTest.BasicEntity.class);
    }

    @Override
    protected BasicDaoTest.BasicEntity createEntityInstance() {
        BasicDaoTest.BasicEntity entityInstance = new BasicDaoTest.BasicEntity();
        entityInstance.setId(1);
        entityInstance.setName("Name");
        return entityInstance;
    }

    @Override
    protected GenericJdbcDao<BasicDaoTest.BasicEntity> createDao() {
        GenericJdbcDao<BasicDaoTest.BasicEntity> result = super.createDao();
        when(result.getJdbcTemplate().getJdbcOperations().query(anyString(), Matchers.<RowMapper<Object>>any(), any(Object.class)))
                .thenReturn(ImmutableList.of());
        when(result.getJdbcTemplate().getJdbcOperations().queryForObject(startsWith("SELECT COUNT(*) FROM"), Matchers.<RowMapper<Long>>any(), any(Object.class)))
                .thenReturn(0L);

        when(result.getJdbcTemplate().query(anyString(), anyMapOf(String.class, Object.class), Matchers.<RowMapper<Object>>any()))
                .thenReturn(ImmutableList.of());
        when(result.getJdbcTemplate().queryForObject(startsWith("SELECT COUNT(*) FROM"), anyMapOf(String.class, Object.class), Matchers.<RowMapper<Long>>any()))
                .thenReturn(0L);
        return result;
    }

    @Test(expected = EmptyResultDataAccessException.class)
    public void testGetById() {
        try {
            dao.getById(2);
        } finally {
            verify(dao.getJdbcTemplate()).query(
                    eq("SELECT `t`.`id`, `t`.`name` FROM `basic_entity` AS `t` WHERE `t`.`id` = :id"),
                    eq(ImmutableMap.of("id", 2)),
                    Matchers.<RowMapper<Object>>any()
            );
        }
    }

    @Test(expected = EmptyResultDataAccessException.class)
    public void testGetByIdMap() {
        try {
            dao.getById(ImmutableMap.of("id", 2));
        } finally {
            verify(dao.getJdbcTemplate()).query(
                    eq("SELECT `t`.`id`, `t`.`name` FROM `basic_entity` AS `t` WHERE `t`.`id` = :id"),
                    eq(ImmutableMap.of("id", 2)),
                    Matchers.<RowMapper<Object>>any()
            );
        }
    }

    @Test(expected = EmptyResultDataAccessException.class)
    public void testGetByCondition() {
        try {
            dao.getByCondition("WHERE id = ?", 2);
        } finally {
            verify(dao.getJdbcTemplate().getJdbcOperations()).query(
                    eq("SELECT `t`.`id`, `t`.`name` FROM `basic_entity` AS `t` WHERE id = ?"),
                    Matchers.<RowMapper<Object>>any(),
                    eq(2)
            );
        }
    }

    @Test(expected = EmptyResultDataAccessException.class)
    public void testGetByConditionMap() {
        try {
            dao.getByCondition("WHERE id = :id", ImmutableMap.of("id", 2));
        } finally {
            verify(dao.getJdbcTemplate()).query(
                    eq("SELECT `t`.`id`, `t`.`name` FROM `basic_entity` AS `t` WHERE id = :id"),
                    eq(ImmutableMap.of("id", 2)),
                    Matchers.<RowMapper<Object>>any()
            );
        }
    }

    @Test(expected = EmptyResultDataAccessException.class)
    public void testGetByQuery() {
        try {
            dao.getByQuery("SELECT * from basic_entity WHERE id = ?", 2);
        } finally {
            verify(dao.getJdbcTemplate().getJdbcOperations()).query(
                    eq("SELECT * from basic_entity WHERE id = ?"),
                    Matchers.<RowMapper<Object>>any(),
                    eq(2)
            );
        }
    }

    @Test(expected = EmptyResultDataAccessException.class)
    public void testGetByQueryMap() {
        try {
            dao.getByQuery("SELECT * from basic_entity WHERE id = :id", ImmutableMap.of("id", 2));
        } finally {
            verify(dao.getJdbcTemplate()).query(
                    eq("SELECT * from basic_entity WHERE id = :id"),
                    eq(ImmutableMap.of("id", 2)),
                    Matchers.<RowMapper<Object>>any()
            );
        }
    }

    @Test
    public void testFindById() {
        Optional<BasicDaoTest.BasicEntity> result = dao.findById(2);

        verify(dao.getJdbcTemplate()).query(
                eq("SELECT `t`.`id`, `t`.`name` FROM `basic_entity` AS `t` WHERE `t`.`id` = :id"),
                eq(ImmutableMap.of("id", 2)),
                Matchers.<RowMapper<Object>>any()
        );

        assertEquals(Optional.empty(), result);
    }

    @Test
    public void testFindByIdMap() {
        Optional<BasicDaoTest.BasicEntity> result = dao.findById(ImmutableMap.of("id", 2));

        verify(dao.getJdbcTemplate()).query(
                eq("SELECT `t`.`id`, `t`.`name` FROM `basic_entity` AS `t` WHERE `t`.`id` = :id"),
                eq(ImmutableMap.of("id", 2)),
                Matchers.<RowMapper<Object>>any()
        );

        assertEquals(Optional.empty(), result);
    }

    @Test
    public void testFindByCondition() {
        Optional<BasicDaoTest.BasicEntity> result = dao.findByCondition("WHERE id = ?", 2);

        verify(dao.getJdbcTemplate().getJdbcOperations()).query(
                eq("SELECT `t`.`id`, `t`.`name` FROM `basic_entity` AS `t` WHERE id = ?"),
                Matchers.<RowMapper<Object>>any(),
                eq(2)
        );

        assertEquals(Optional.empty(), result);
    }

    @Test
    public void testFindByConditionMap() {
        Optional<BasicDaoTest.BasicEntity> result = dao.findByCondition("WHERE id = :id", ImmutableMap.of("id", 2));

        verify(dao.getJdbcTemplate()).query(
                eq("SELECT `t`.`id`, `t`.`name` FROM `basic_entity` AS `t` WHERE id = :id"),
                eq(ImmutableMap.of("id", 2)),
                Matchers.<RowMapper<Object>>any()
        );

        assertEquals(Optional.empty(), result);
    }

    @Test
    public void testFindByQuery() {
        Optional<BasicDaoTest.BasicEntity> result = dao.findByQuery("SELECT * from basic_entity WHERE id = ?", 2);

        verify(dao.getJdbcTemplate().getJdbcOperations()).query(
                eq("SELECT * from basic_entity WHERE id = ?"),
                Matchers.<RowMapper<Object>>any(),
                eq(2)
        );

        assertEquals(Optional.empty(), result);
    }

    @Test
    public void testFindByQueryMap() {
        Optional<BasicDaoTest.BasicEntity> result = dao.findByQuery("SELECT * from basic_entity WHERE id = :id", ImmutableMap.of("id", 2));

        verify(dao.getJdbcTemplate()).query(
                eq("SELECT * from basic_entity WHERE id = :id"),
                eq(ImmutableMap.of("id", 2)),
                Matchers.<RowMapper<Object>>any()
        );

        assertEquals(Optional.empty(), result);
    }

    @Test
    public void testFindAll() {
        List<BasicDaoTest.BasicEntity> result = dao.findAll();

        verify(dao.getJdbcTemplate()).query(
                eq("SELECT `t`.`id`, `t`.`name` FROM `basic_entity` AS `t`"),
                eq(ImmutableMap.of()),
                Matchers.<RowMapper<Object>>any()
        );

        assertEquals(ImmutableList.of(), result);
    }

    @Test
    public void testFindAllByCondition() {
        List<BasicDaoTest.BasicEntity> result = dao.findAllByCondition("WHERE name = ?", "NotExisting");

        verify(dao.getJdbcTemplate().getJdbcOperations()).query(
                eq("SELECT `t`.`id`, `t`.`name` FROM `basic_entity` AS `t` WHERE name = ?"),
                Matchers.<RowMapper<Object>>any(),
                eq("NotExisting")
        );

        assertEquals(ImmutableList.of(), result);
    }

    @Test
    public void testFindAllByConditionMap() {
        List<BasicDaoTest.BasicEntity> result = dao.findAllByCondition("WHERE name = :name", ImmutableMap.of("name", "NotExisting"));

        verify(dao.getJdbcTemplate()).query(
                eq("SELECT `t`.`id`, `t`.`name` FROM `basic_entity` AS `t` WHERE name = :name"),
                eq(ImmutableMap.of("name", "NotExisting")),
                Matchers.<RowMapper<Object>>any()
        );

        assertEquals(ImmutableList.of(), result);
    }

    @Test
    public void testFindAllByQuery() {
        List<BasicDaoTest.BasicEntity> result = dao.findAllByQuery("SELECT * FROM basic_entity WHERE name = ?", "NotExisting");

        verify(dao.getJdbcTemplate().getJdbcOperations()).query(
                eq("SELECT * FROM basic_entity WHERE name = ?"),
                Matchers.<RowMapper<Object>>any(),
                eq("NotExisting")
        );

        assertEquals(ImmutableList.of(), result);
    }

    @Test
    public void testFindAllByQueryMap() {
        List<BasicDaoTest.BasicEntity> result = dao.findAllByQuery("SELECT * FROM basic_entity WHERE name = :name", ImmutableMap.of("name", "NotExisting"));

        verify(dao.getJdbcTemplate()).query(
                eq("SELECT * FROM basic_entity WHERE name = :name"),
                eq(ImmutableMap.of("name", "NotExisting")),
                Matchers.<RowMapper<Object>>any()
        );

        assertEquals(ImmutableList.of(), result);
    }

    @Test
    public void testCount() {
        long result = dao.count();

        verify(dao.getJdbcTemplate()).queryForObject(
                eq("SELECT COUNT(*) FROM `basic_entity` AS `t`"),
                eq(ImmutableMap.of()),
                Matchers.<RowMapper<Long>>any()
        );

        assertEquals(0L, result);
    }

    @Test
    public void testCountByCondition() {
        long result = dao.countByCondition("WHERE name = ?", "NotExisting");

        verify(dao.getJdbcTemplate().getJdbcOperations()).queryForObject(
                eq("SELECT COUNT(*) FROM `basic_entity` AS `t` WHERE name = ?"),
                Matchers.<RowMapper<Long>>any(),
                eq("NotExisting")
        );

        assertEquals(0L, result);
    }

    @Test
    public void testCountByConditionMap() {
        long result = dao.countByCondition("WHERE name = :name", ImmutableMap.of("name", "NotExisting"));

        verify(dao.getJdbcTemplate()).queryForObject(
                eq("SELECT COUNT(*) FROM `basic_entity` AS `t` WHERE name = :name"),
                eq(ImmutableMap.of("name", "NotExisting")),
                Matchers.<RowMapper<Long>>any()
        );

        assertEquals(0L, result);
    }

    @Test
    public void testCountByQuery() {
        long result = dao.countByQuery("SELECT COUNT(*) FROM basic_entity WHERE name = ?", "NotExisting");

        verify(dao.getJdbcTemplate().getJdbcOperations()).queryForObject(
                eq("SELECT COUNT(*) FROM basic_entity WHERE name = ?"),
                Matchers.<RowMapper<Long>>any(),
                eq("NotExisting")
        );

        assertEquals(0L, result);
    }

    @Test
    public void testCountByQueryMap() {
        long result = dao.countByQuery("SELECT COUNT(*) FROM basic_entity WHERE name = :name", ImmutableMap.of("name", "NotExisting"));

        verify(dao.getJdbcTemplate()).queryForObject(
                eq("SELECT COUNT(*) FROM basic_entity WHERE name = :name"),
                eq(ImmutableMap.of("name", "NotExisting")),
                Matchers.<RowMapper<Long>>any()
        );

        assertEquals(0L, result);
    }
}
