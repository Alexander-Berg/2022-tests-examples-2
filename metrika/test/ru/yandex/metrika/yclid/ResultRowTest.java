package ru.yandex.metrika.yclid;

import org.junit.Ignore;

import ru.yandex.metrika.util.chunk.ch2.CHOrmUtils;

@Ignore
public class ResultRowTest {

    public static void main(String[] args) {
        String chMergeTreeCreateTable = CHOrmUtils.getCHReplicatedMergeTreeCreateTable(ResultRow.class, "testtable",
                "testdb");
        String fullCreateTable = CHOrmUtils.getCreateTable(ResultRow.class, "testtable", chMergeTreeCreateTable, true);
        System.out.println(fullCreateTable);
    }
}
