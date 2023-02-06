package ru.yandex.metrika.topsites.task.topsites;

import java.util.Arrays;
import java.util.Collection;
import java.util.Set;

import com.google.common.collect.Sets;
import org.joda.time.LocalDate;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.mockito.ArgumentCaptor;

import ru.yandex.bolts.collection.Cf;
import ru.yandex.bolts.collection.ListF;
import ru.yandex.inside.yt.kosher.cypress.YPath;
import ru.yandex.metrika.api.topsites.snapshot.SnapshotDBInfo;
import ru.yandex.metrika.api.topsites.snapshot.SnapshotInfo;
import ru.yandex.metrika.api.topsites.snapshot.SnapshotStatus;
import ru.yandex.metrika.api.topsites.snapshot.TopSitesSnapshotsDatabase;

import static org.junit.Assert.assertEquals;
import static org.mockito.Mockito.doReturn;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;

@RunWith(Parameterized.class)
public class TopSitesSnapshotCleanerTaskTest {

    private static final YPath rootPath = YPath.simple("//home/radar_top_sites/testing/some/root/path");
    private static final ListF<SnapshotInfo> snapshotsInDatabase = Cf.list(
            new SnapshotInfo("2018-06-05_123456789"),
            new SnapshotInfo("2018-06-06_123456789"),
            new SnapshotInfo("2018-06-07_123456789"),
            new SnapshotInfo("2018-06-08_123456789"),
            new SnapshotInfo("2018-06-09_123456789"),
            new SnapshotInfo("2018-05-31_123456789"),
            new SnapshotInfo("2018-05-31_123456785", new LocalDate(2018, 5, 2)),
            new SnapshotInfo("2018-05-30_123456789"),
            new SnapshotInfo("2018-04-30_123456789"),
            new SnapshotInfo("2018-03-31_123456789"),
            new SnapshotInfo("2018-03-30_123456789"));

    @Parameterized.Parameter
    public int snapshotsToRetain;

    @Parameterized.Parameter(1)
    public boolean retainMonthly;

    @Parameterized.Parameter(2)
    public Set<String> expectedDeletes;

    @Parameterized.Parameters(name = "params: {0}, {1}")
    public static Collection<Object[]> createParameters() {
        return Arrays.asList(
                new Object[][]{
                        {3, true, Sets.newHashSet("2018-03-30_123456789", "2018-05-30_123456789", "2018-05-31_123456785", "2018-06-05_123456789", "2018-06-06_123456789")},
                        {3, false, Sets.newHashSet("2018-05-31_123456789", "2018-04-30_123456789", "2018-05-31_123456785", "2018-03-31_123456789", "2018-03-30_123456789", "2018-05-30_123456789", "2018-06-05_123456789", "2018-06-06_123456789")},
                        {5, false, Sets.newHashSet("2018-05-31_123456789", "2018-04-30_123456789", "2018-05-31_123456785", "2018-03-31_123456789", "2018-03-30_123456789", "2018-05-30_123456789")}
                }
        );
    }

    @Test
    public void snapshotsToDelete() {
        TopSitesSnapshotsDatabase snapshotsDatabase = mock(TopSitesSnapshotsDatabase.class);
        ListF<SnapshotDBInfo> dbInfoList = snapshotsInDatabase.map(s -> new SnapshotDBInfo(s, SnapshotStatus.READY, rootPath.child(s.getName())));
        doReturn(dbInfoList).when(snapshotsDatabase).listReady();

        TopSitesSnapshotCleanerTask cleanerTask = new TopSitesSnapshotCleanerTask(snapshotsDatabase, retainMonthly);
        cleanerTask.setLastSnapshotsToRetain(snapshotsToRetain);
        cleanerTask.execute();

        ArgumentCaptor<String> markForDeleteCaptor = ArgumentCaptor.forClass(String.class);
        verify(snapshotsDatabase, times(expectedDeletes.size())).markForDelete(markForDeleteCaptor.capture());

        Set<String> capturedDeletes = Sets.newHashSet(markForDeleteCaptor.getAllValues());
        assertEquals(expectedDeletes, capturedDeletes);
    }
}
