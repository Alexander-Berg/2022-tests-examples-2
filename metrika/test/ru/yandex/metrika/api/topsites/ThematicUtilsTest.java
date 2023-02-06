package ru.yandex.metrika.api.topsites;

import java.util.List;
import java.util.Map;
import java.util.Set;

import com.google.common.collect.ImmutableMap;
import com.google.common.collect.ImmutableSet;
import org.junit.Test;

import ru.yandex.metrika.api.topsites.model.Thematic;

import static com.google.common.collect.ImmutableList.of;
import static org.assertj.core.api.Assertions.assertThat;

public class ThematicUtilsTest {

    private static final Set<List<String>> EXPANDED_THEMATIC_IDS = ImmutableSet.of(
            of("t1"),
            of("t2"),
            of("t1", "t11"),
            of("t1", "t12"),
            of("t2", "t21")
    );

    private static final Set<List<String>> COLLAPSED_THEMATIC_IDS = ImmutableSet.of(
            of("t1", "t11"),
            of("t1", "t12"),
            of("t2", "t21")
    );

    private static final Thematic T11 = new Thematic("t11", "T11", false, of());
    private static final Thematic T12 = new Thematic("t12", "T12", false, of());
    private static final Thematic T1 = new Thematic("t1", "T1", false, of(T11, T12));
    private static final Thematic T21 = new Thematic("t21", "T21", false, of());
    private static final Thematic T2 = new Thematic("t2", "T2", false, of(T21));
    private static final List<Thematic> THEMATICS = of(T1, T2);

    private static final Map<List<String>, Thematic> THEMATICS_FLAT_MAP = ImmutableMap.of(
            of("t1"), T1,
            of("t1", "t11"), T11,
            of("t1", "t12"), T12,
            of("t2"), T2,
            of("t2", "t21"), T21
    );

    private static final List<List<String>> INTERSECT_THEMATIC_IDS = of(of("t1", "t11"), of("t2"));

    private static final Thematic INTERSECTED_T11 = new Thematic(T11, of());
    private static final Thematic INTERSECTED_T1 = new Thematic(T1, of(INTERSECTED_T11));
    private static final Thematic INTERSECTED_T2 = new Thematic(T2, of());
    private static final List<Thematic> INTERSECTED_THEMATICS = of(INTERSECTED_T1, INTERSECTED_T2);

    @Test
    public void expandThematicIds() {
        assertThat(ThematicUtils.expandThematicIds(COLLAPSED_THEMATIC_IDS)).isEqualTo(EXPANDED_THEMATIC_IDS);
    }
    @Test
    public void expandThematicIdsAlreadyExpanded() {
        assertThat(ThematicUtils.expandThematicIds(EXPANDED_THEMATIC_IDS)).isEqualTo(EXPANDED_THEMATIC_IDS);
    }

    @Test
    public void collapseThematicIds() {
        assertThat(ThematicUtils.collapseThematicIds(EXPANDED_THEMATIC_IDS)).isEqualTo(COLLAPSED_THEMATIC_IDS);
    }

    @Test
    public void collapseThematicIdsAlreadyCollapsed() {
        assertThat(ThematicUtils.collapseThematicIds(COLLAPSED_THEMATIC_IDS)).isEqualTo(COLLAPSED_THEMATIC_IDS);
    }

    @Test
    public void getThematicsFlatMap() {
        assertThat(ThematicUtils.getThematicsFlatMap(THEMATICS)).isEqualTo(THEMATICS_FLAT_MAP);
    }

    @Test
    public void intersectThematics() {
        assertThat(ThematicUtils.intersectThematics(THEMATICS, INTERSECT_THEMATIC_IDS))
                .usingRecursiveFieldByFieldElementComparator()
                .isEqualTo(INTERSECTED_THEMATICS);
    }
}
