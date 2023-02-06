package ru.yandex.metrika.userparams2d;

import java.io.IOException;

import org.junit.Before;
import org.junit.Test;

import ru.yandex.metrika.api.management.client.external.userparams.UserParamUpdate;
import ru.yandex.metrika.lb.write.LogbrokerWriterStub;
import ru.yandex.metrika.userparams2d.tasks.onetime.UserparamsReuploader;
import ru.yandex.metrika.userparams2d.tasks.onetime.UserparamsReuploader.CsvParam;

public class UserparamsReuploaderTest {

    private final LogbrokerWriterStub<UserParamUpdate> downstreamStub = new LogbrokerWriterStub<>();
    private UserparamsReuploader reuploader;

    CsvParam param1 = new CsvParam(42, 123321, "some_client_id", "", "", "", "", "", "", "", "", "", "", 0.);
    CsvParam param2 = new CsvParam(42, 123321, "", "1", "2", "3", "4", "5", "6", "7", "8", "9", "", 9.);

    @Before
    public void init() {
        reuploader = new UserparamsReuploader(downstreamStub);
    }

    @Test
    public void test() throws IOException {
//        reuploader.reupload("/Users/vtal9/Library/Application Support/JetBrains/IntelliJIdea2021.2/scratches/clickhouse/datatest.csv");
//        downstreamStub.assertHaveOnlyMessages(param1.toUpdate(), param2.toUpdate());
//        System.out.println(downstreamStub.getMessages());
    }
}
