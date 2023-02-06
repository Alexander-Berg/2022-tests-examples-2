package ru.yandex.metrika.mobile.push.api.steps;

import java.io.IOException;

import com.amazonaws.services.s3.AmazonS3;
import com.amazonaws.services.s3.model.S3Object;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

import ru.yandex.metrika.dbclients.mds.MdsS3Properties;
import ru.yandex.metrika.util.io.IOUtils;
import ru.yandex.metrika.util.io.UncheckedIOException;
import ru.yandex.qatools.allure.annotations.Step;

@Component
public class LogsSteps {

    @Autowired
    private AmazonS3 mdsS3Client;
    @Autowired
    private MdsS3Properties mdsS3Properties;

    @Step("Добавление группы")
    public String get(String key) {
        try (S3Object object = mdsS3Client.getObject(mdsS3Properties.getPushLogBucket(), key)) {
            return IOUtils.toString(object.getObjectContent());
        } catch (IOException ex) {
            throw new UncheckedIOException(ex);
        }
    }
}
