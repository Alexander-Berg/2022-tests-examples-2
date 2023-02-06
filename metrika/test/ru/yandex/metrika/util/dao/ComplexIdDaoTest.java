package ru.yandex.metrika.util.dao;

import java.util.Map;
import java.util.Objects;

import com.google.common.collect.ImmutableMap;
import org.junit.Test;
import org.mockito.hamcrest.MockitoHamcrest;
import org.springframework.jdbc.core.namedparam.SqlParameterSource;

import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.hasProperty;
import static org.mockito.Matchers.eq;
import static org.mockito.Mockito.verify;

public class ComplexIdDaoTest extends GenericJdbcDaoTestBase<ComplexIdDaoTest.ComplexIdEntity> {

    public ComplexIdDaoTest() {
        super(ComplexIdEntity.class);
    }

    @Override
    protected ComplexIdEntity createEntityInstance() {
        ComplexIdEntity entityInstance = new ComplexIdEntity();
        entityInstance.setFirstId(1);
        entityInstance.setSecondId(2);
        entityInstance.setName("Name");
        return entityInstance;
    }

    @Test
    public void testUpdate() {
        dao.update(entityInstance);

        verify(dao.getJdbcTemplate()).update(
                eq("UPDATE `complex_id_entity` AS `t` SET `t`.`name` = :name WHERE `t`.`first_id` = :firstId AND `t`.`second_id` = :secondId"),
                MockitoHamcrest.<SqlParameterSource>argThat(hasProperty("values", equalTo(ImmutableMap.<String, Object>builder()
                        .put("firstId", 1)
                        .put("secondId", 2)
                        .put("name", "Name")
                        .build()
                )))
        );
    }

    @Test
    public void testUpdateMap() {
        dao.update(Map.of("name", "Name"), 1, 2);

        verify(dao.getJdbcTemplate()).update(
                eq("UPDATE `complex_id_entity` AS `t` SET `t`.`name` = :name WHERE `t`.`first_id` = :firstId AND `t`.`second_id` = :secondId"),
                MockitoHamcrest.<SqlParameterSource>argThat(hasProperty("values", equalTo(ImmutableMap.<String, Object>builder()
                        .put("firstId", 1)
                        .put("secondId", 2)
                        .put("name", "Name")
                        .build()
                )))
        );
    }

    @Table(ComplexIdEntity.TABLE_NAME)
    public static class ComplexIdEntity {

        public static final String TABLE_NAME = "complex_id_entity";

        @Id
        private int firstId;

        @Id
        private int secondId;

        private String name;

        public int getFirstId() {
            return firstId;
        }

        public void setFirstId(int firstId) {
            this.firstId = firstId;
        }

        public int getSecondId() {
            return secondId;
        }

        public void setSecondId(int secondId) {
            this.secondId = secondId;
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
            ComplexIdEntity that = (ComplexIdEntity) o;
            return firstId == that.firstId &&
                    secondId == that.secondId &&
                    Objects.equals(name, that.name);
        }

        @Override
        public int hashCode() {
            return Objects.hash(firstId, secondId, name);
        }
    }
}
