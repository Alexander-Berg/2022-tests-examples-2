package ru.yandex.metrika.tool.visits;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.Arrays;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;

import ru.yandex.metrika.util.Patterns;

/**
 * анализирует количество записанных визитов в дне, в метрике и в визоре.
 * в идеале должно иметь место следующее:
 * 1. для всех сайтов, у которых меньше 1000 визитов за день мы записали все визиты
 * 2. для всех сайтов у которых больше 1000 визитов в день, мы записали 1000 визитов. ровно.
 *
 * два файла содержат tab separated значения из визора и метрики на пятом слое за 2011-04-07.
 * result2 получен из результатов запроса
SELECT * FROM (
SELECT counterId, COUNT(*) cc FROM WV_5_0.visits WHERE dayNumber = 1192 GROUP BY counterId UNION ALL
SELECT counterId, COUNT(*) cc FROM WV_5_1.visits WHERE dayNumber = 1192 GROUP BY counterId UNION ALL
SELECT counterId, COUNT(*) cc FROM WV_5_2.visits WHERE dayNumber = 1192 GROUP BY counterId UNION ALL
SELECT counterId, COUNT(*) cc FROM WV_5_3.visits WHERE dayNumber = 1192 GROUP BY counterId UNION ALL
SELECT counterId, COUNT(*) cc FROM WV_5_4.visits WHERE dayNumber = 1192 GROUP BY counterId UNION ALL
SELECT counterId, COUNT(*) cc FROM WV_5_5.visits WHERE dayNumber = 1192 GROUP BY counterId UNION ALL
SELECT counterId, COUNT(*) cc FROM WV_5_6.visits WHERE dayNumber = 1192 GROUP BY counterId UNION ALL
SELECT counterId, COUNT(*) cc FROM WV_5_7.visits WHERE dayNumber = 1192 GROUP BY counterId UNION ALL
SELECT counterId, COUNT(*) cc FROM WV_5_8.visits WHERE dayNumber = 1192 GROUP BY counterIdUNION ALL
SELECT counterId, COUNT(*) cc FROM WV_5_9.visits WHERE dayNumber = 1192 GROUP BY counterId) zz
ORDER BY cc DESC, counterId;

 * result получен из олапа с помощью запроса

<?xml version='1.0' encoding='utf-8' ?>
<olap_query version="1.0">
    <format>tab</format>
    <counter_id>0</counter_id>
    <dates>
        <first>2011-04-07</first>
        <last>2011-04-07</last>
    </dates>
    <keys>
        <attribute>CounterID</attribute>
    </keys>
    <aggregates>
        <aggregate>
            <attribute>DummyAttribute</attribute>
            <function>count</function>
        </aggregate>
    </aggregates>
    <sort>
        <column>
            <index>2</index>
            <direction>descending</direction>
        </column>
    </sort>
</olap_query>

 * сами файлы не под контролем версий, ибо в них по мегабайту текста
 *
 *
 вывод написанной ниже программы на этих данных:
 keys in metr = 92350
 keys in visor = 92028
 keys not in metr = 58

 errorsPos = 3382 distr = [52955, 12509, 5804, 3706, 2458, 1930, 1401, 1135, 904, 805, 676, 553, 473, 423, 380, 355, 306, 302, 266, 219]
 errorsNeg = 8 distr = [420, 226, 126, 72, 45, 39, 31, 19, 14, 9, 8, 2, 0, 3, 3, 1, 1, 0, 0, 1]

 вот так-то.
 * @author orantius
 * @version $Id$
 * @since 4/8/11
 */
public class QualityMeasure {
    public static void main(String[] args) throws Exception{
        Map<Integer, Integer> metr = readMap("src/java/ru/yandex/metrika/tool/visits/result.tsv");
        System.out.println("keys in metr = " + metr.size());

        Map<Integer, Integer> visor = readMap("src/java/ru/yandex/metrika/tool/visits/result2.tsv");
        System.out.println("keys in visor = " + visor.size());

        Set<Integer> filterCounters = readSet("src/java/ru/yandex/metrika/tool/visits/result3.tsv");
        System.out.println("keys in visor = " + visor.size());

        Set<Integer> notInMetr = new HashSet<>();  // V \ M
        for (Map.Entry<Integer, Integer> ee : visor.entrySet()) {
            if (!metr.containsKey(ee.getKey())) {
                notInMetr.add(ee.getKey());
            }
        }
        System.out.println("keys not in metr = " + notInMetr.size());

        int[] distrPos = new int[10];
        int[] distrNeg = new int[10];
        int errorsPos = 0;
        int errorsNeg = 0;
        for (Map.Entry<Integer, Integer> ee : metr.entrySet()) {
            if (visor.containsKey(ee.getKey()) && !filterCounters.contains(ee.getKey())) {  // V * M && фильтров для счетчика нет.
                Integer metrVisits = ee.getValue();
                Integer visorVisits = visor.get(ee.getKey());
                int diff = Math.min(1000, metrVisits) - visorVisits;
                if(Math.abs(diff) > 100) {
                    System.out.println(", " + ee.getKey()+ ' ' +visorVisits+ ' ' +metrVisits);
                }

                if (diff < -distrNeg.length) {
                    errorsNeg++;
                } else if (diff < 0) {
                    distrNeg[-1-diff]++;
                } else if (diff < distrPos.length) {
                    distrPos[diff]++;
                } else {
                    errorsPos++;
                }

            }
        }
        System.out.println("errorsPos = " + errorsPos + " distr = " + Arrays.toString(distrPos));
        System.out.println("errorsNeg = " + errorsNeg + " distr = " + Arrays.toString(distrNeg));

    }

    private static Set<Integer> readSet(String pathname) throws IOException {
        Set<Integer> mpa = new HashSet<>();
        File file = new File(pathname);
        BufferedReader fis = new BufferedReader(new InputStreamReader(new FileInputStream(file)));
        String s = null;
        while ((s = fis.readLine())!=null) {
            int element = Integer.parseInt(s);
            mpa.add(element);
        }
        return mpa;
    }

    private static Map<Integer,Integer> readMap(String pathname) throws IOException {
        Map<Integer,Integer> mpa = new HashMap<>();
        File file = new File(pathname);
        BufferedReader fis = new BufferedReader(new InputStreamReader(new FileInputStream(file)));
        String s = null;
        while ((s = fis.readLine())!=null) {
            String[] split = Patterns.TAB.split(s);
            int key = Integer.parseInt(split[0]);
            int value = Integer.parseInt(split[1]);
            mpa.put(key, value);
        }
        return mpa;
    }
}
