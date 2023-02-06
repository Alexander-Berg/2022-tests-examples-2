package ru.yandex.metrika.util.dao;

import com.google.common.collect.ImmutableList;
import org.junit.Before;
import org.junit.Ignore;
import org.mockito.Matchers;
import org.springframework.jdbc.core.JdbcOperations;
import org.springframework.jdbc.core.RowMapper;
import org.springframework.jdbc.core.namedparam.NamedParameterJdbcTemplate;
import org.springframework.jdbc.core.namedparam.SqlParameterSource;
import org.springframework.jdbc.support.KeyHolder;

import static org.mockito.Matchers.any;
import static org.mockito.Matchers.anyMapOf;
import static org.mockito.Matchers.anyString;
import static org.mockito.Matchers.startsWith;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

@Ignore
public abstract class GenericJdbcDaoTestBase<T> {

    protected JdbcMetadataGenerator jdbcMetadataGenerator = new JdbcMetadataGenerator();
    protected Class<T> entityClass;
    protected GenericJdbcDao<T> dao;
    protected T entityInstance;

    protected GenericJdbcDaoTestBase(Class<T> entityClass) {
        this.entityClass = entityClass;
    }

    @Before
    public void init() {
        entityInstance = createEntityInstance();
        dao = createDao();
    }

    protected abstract T createEntityInstance();

    protected GenericJdbcDao<T> createDao() {
        JdbcOperations jdbcOperations = mock(JdbcOperations.class);
        when(jdbcOperations.update(anyString(), any(Object.class))).thenReturn(1);
        when(jdbcOperations.query(anyString(), Matchers.<RowMapper<Object>>any(), any(Object.class)))
                .thenReturn(ImmutableList.of(entityInstance));
        when(jdbcOperations.queryForObject(startsWith("SELECT COUNT(*) FROM"), Matchers.<RowMapper<Long>>any(), any(Object.class)))
                .thenReturn(1L);

        NamedParameterJdbcTemplate jdbcTemplate = mock(NamedParameterJdbcTemplate.class);
        when(jdbcTemplate.getJdbcOperations()).thenReturn(jdbcOperations);
        when(jdbcTemplate.update(anyString(), any(SqlParameterSource.class), any(KeyHolder.class))).thenReturn(1);
        when(jdbcTemplate.update(anyString(), anyMapOf(String.class, Object.class))).thenReturn(1);
        when(jdbcTemplate.query(anyString(), anyMapOf(String.class, Object.class), Matchers.<RowMapper<Object>>any()))
                .thenReturn(ImmutableList.of(entityInstance));
        when(jdbcTemplate.queryForObject(startsWith("SELECT COUNT(*) FROM"), anyMapOf(String.class, Object.class), Matchers.<RowMapper<Long>>any()))
                .thenReturn(1L);

        GenericJdbcDao<T> dao = new GenericJdbcDao<>(entityClass, jdbcMetadataGenerator, jdbcTemplate);
        dao.init();

        return dao;
    }
}
