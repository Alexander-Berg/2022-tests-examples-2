package ru.yandex.metrika.util.collections;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Random;

import org.junit.Before;
import org.junit.Test;

import static junit.framework.Assert.assertTrue;

/**
 * @author jkee
 */

public class WeightedSorterTest {

    private WeightedSorter<SortEntity> weightedSorter;

    @Before
    public void setUp() throws Exception {
        weightedSorter = new WeightedSorter<>(
                new WeightedSorter.InfluenceExtractor<SortEntity>() {
                    @Override
                    public double getFactor(SortEntity object) {
                        return object.visits;
                    }
                },
                new WeightedSorter.MainExtractor<SortEntity>() {
                    @Override
                    public double getValue(SortEntity object) {
                        return object.conversion;
                    }
                }
        );
        weightedSorter.setTrustFunction(WeightedSorter.sqrtTrustFunction(1));
    }

    static class SortEntity {
        final long visits;
        final double conversion;
        final boolean good;

        private SortEntity(long visits, double conversion) {
            this.visits = visits;
            this.conversion = conversion;
            good = false;
        }

        private SortEntity(long visits, double conversion, boolean good) {
            this.visits = visits;
            this.conversion = conversion;
            this.good = good;
        }

        @Override
        public String toString() {
            return "SortEntity{" +
                    "visits=" + visits +
                    ", conversion=" + conversion +
                    ", good=" + good +
                    '}';
        }
    }

    @Test
    public void testSort() throws Exception {
        List<SortEntity> sortEntityList = new ArrayList<>();
        Random rand = new Random(11000);
        for (int i = 0; i < 1000; i++) {
            sortEntityList.add(new SortEntity(rand.nextInt(1000) + 4000, rand.nextDouble() + 20));
        }
        /*большая достоверность, ненамного больше значение*/
        for (int i = 0; i < 10; i++) {
            sortEntityList.add(new SortEntity(rand.nextInt(1000) + 9000, rand.nextDouble() + 25, true));
        }
        /*средняя достоверность, ненамного больше значение*/
        for (int i = 0; i < 10; i++) {
            sortEntityList.add(new SortEntity(rand.nextInt(1000) + 4000, rand.nextDouble() + 25, true));
        }
        /*слабая достоверность, значительно большее значение - попасть не должны*/
        for (int i = 0; i < 10; i++) {
            sortEntityList.add(new SortEntity(50, rand.nextDouble() + 100));
        }
        weightedSorter.sort(sortEntityList, true);
        for (int i = 0; i < 20; i++) {
            System.out.println(sortEntityList.get(i));
            //assertTrue(sortEntityList.get(i).good);
        }
        weightedSorter.sort(sortEntityList, false);
        for (int i = 0; i < 50; i++) {
            //System.out.println(sortEntityList.get(i));
        }

    }


    @Test
    public void testSortEqualValue() throws Exception {
        List<SortEntity> sortEntityList = new ArrayList<>();
        Random rand = new Random(3213124);
        for (int i = 10; i < 100; i++) {
            sortEntityList.add(new SortEntity(i, 50));
        }
        Collections.shuffle(sortEntityList, rand);
        weightedSorter.sort(sortEntityList, 50, 500, false);
        for (SortEntity sortEntity : sortEntityList) {
            System.out.println(sortEntity);
        }
        SortEntity current = sortEntityList.get(0);
        for (int i = 1; i < sortEntityList.size(); i++) {
            SortEntity next = sortEntityList.get(i);
            assertTrue(current.visits + " " + next.visits, current.visits > next.visits);
            current = next;
        }
    }

    @Test
    public void testSortEqualVisits() throws Exception {
        List<SortEntity> sortEntityList = new ArrayList<>();
        Random rand = new Random(3213124);
        for (int i = 0; i < 10; i++) {
            sortEntityList.add(new SortEntity(50, i));
        }
        Collections.shuffle(sortEntityList, rand);
        weightedSorter.sort(sortEntityList, 50, 500, false);
        for (SortEntity sortEntity : sortEntityList) {
            System.out.println(sortEntity);
        }
        SortEntity current = sortEntityList.get(0);
        for (int i = 1; i < sortEntityList.size(); i++) {
            SortEntity next = sortEntityList.get(i);
            assertTrue(next.conversion > current.conversion);
            current = next;
        }
    }
}
