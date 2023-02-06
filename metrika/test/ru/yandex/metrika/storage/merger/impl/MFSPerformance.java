package ru.yandex.metrika.storage.merger.impl;

import java.io.File;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Calendar;
import java.util.Collections;
import java.util.Date;
import java.util.List;
import java.util.Random;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import ru.yandex.metrika.storage.merger.ChunkWriter;
import ru.yandex.metrika.storage.merger.ItemBuffer;
import ru.yandex.metrika.storage.merger.ItemFilter;
import ru.yandex.metrika.storage.merger.ValueReader;
import ru.yandex.metrika.storage.merger.iterator.ClosingIterator;
import ru.yandex.metrika.util.log.Log4jSetup;
import ru.yandex.metrika.util.log.LogTimer;

import static ru.yandex.metrika.storage.merger.impl.MergedFileSetImplTest.createMerger;
import static ru.yandex.metrika.storage.merger.impl.MergedFileSetImplTest.descount;

/** @author jkee */
public class MFSPerformance {

    private static final Logger log = LoggerFactory.getLogger(MFSPerformance.class);

    private static int entryCount = (int) 10.0e6;

    public static void main(String[] args) throws IOException {
        if (args.length > 1) entryCount = Integer.parseInt(args[1]);

        /* 1 000 000 entries - 42 mb */
        /* Создаем по 100 000 объектов, так хорошо влазит в оперативку. дальше мержим
        * Команда для сброса кэша fs: echo 3 | sudo tee /proc/sys/vm/drop_caches
        *
        *  Data size: 450 Mb - notebook, ssd
        *                           Hash                Sparse
        *  Create time              101s                48s
        *  Index size:              300 Mb              2Mb
        *  Read time (no fs cache)  12s                 7s
        *  Read time (fs cache)     1600ms              1800ms
        *
        *  Data size: 450 Mb - mtweb02t, hdd
        *                           Hash                Sparse
        *  Create time              60.8s               24.8s
        *  Index size:              300 Mb              2Mb
        *  Read time (no fs cache)  156s                60s
        *  Read time (fs cache)     1880ms              1680ms
        *
        *  Data size: 4.7Gb - notebook, ssd
        *                           Hash                Sparse
        *  Create time              1200s               620s
        *  Index size               2.4Gb               20M
        *  Read time (no fs cache)  10.7s               7.1s
        *  Read time (fs cache)     1.7s                1.9s
        *
        *  Data size: 4.7Gb - mtweb02t, hdd
        *                           Hash                Sparse
        *  Create time              830s                320s
        *  Index size               2.4Gb               20M
        *  Read time (no fs cache)  225s                72.6s
        *  Read time (fs cache)     2s                  1.5s
        *
        * */
        Log4jSetup.basicSetup();
        if ("create".equals(args[0])) {
            log.info("Creating...");
            LogTimer timer = LogTimer.startProcess(MFSPerformance.class, "hash");
            createSet(new File("/opt/yandex/mfstest/hash"), false);
            timer.setProcessEnd();
            timer.setProcessStart("sparse");
            createSet(new File("/opt/yandex/mfstest/sparse"), true);
            timer.setProcessEnd();
        }
        if ("readtest".equals(args[0])) {
            testRead(new File("/opt/yandex/mfstest/hash"), false);
            testRead(new File("/opt/yandex/mfstest/sparse"), true);
        }
    }

    private static void testRead(File file, boolean sparse) throws IOException {
        descount = 0;
        //читаем рандомно 10000 разных индексов
        List<Integer> indexes = new ArrayList<>();
        for (int i = 1; i < 10000; i++) {
            indexes.add( (entryCount / 10000) * i);
        }
        Collections.shuffle(indexes, new Random(1001));
        MergedFileSetImpl merger = createMerger(file, sparse, 10, 4);
        ValueReader<StoredEntity, Integer> reader = merger.getReader(StoredEntity.class);
        LogTimer timer = LogTimer.startProcess(
                MFSPerformance.class, "Reading: " + file.getAbsolutePath() + " sparse: " + sparse);
        for (Integer index : indexes) {
            ClosingIterator<StoredEntity> iterator = reader.valuesForKey(index,
                    ItemFilter.EmptyItemFilter.<StoredEntity>getInstance());
            int count = 0;
            while(iterator.hasNext()) {
                if (iterator.next().counterId != index) log.info("INDEX MISMATCH: {}", index);
                count++;
            }
            iterator.close();
            if (count != 1) log.info("COUNT != 1: {} : {}", count, index);
        }
        timer.setProcessEnd();
        System.out.println(descount);
    }

    private static void createSet(File file, boolean sparse) throws IOException {
        System.out.println(file.getAbsolutePath());
        MergedFileSetImpl merger = createMerger(file, sparse, 10, 4);

        int bigPartsCount = entryCount / 100000;
        for (int i = 0; i < bigPartsCount; i++) {
            ChunkWriter writer = merger.createWriter(new Date());
            ItemBuffer<StoredEntity> buffer =  writer.getItemBuffer(StoredEntity.class);
            Calendar c = Calendar.getInstance();
            c.set(2011, 1, 1);
            for (int j = 0; j < 100000; j++) {
                if (j + i*100000 == 0) continue;
                buffer.put(new StoredEntity(j + i * 100000, 1, c.getTime(), "In the rear with the gear"));
            }
            writer.commit();
        }
        merger.mergeForced();
    }

}
