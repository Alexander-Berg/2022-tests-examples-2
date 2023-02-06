package ru.yandex.taxi.conversation;

import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.context.TestConfiguration;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.context.annotation.Import;

import ru.yandex.market.common.mds.s3.client.service.api.MdsS3Client;
import ru.yandex.market.javaframework.main.config.SpringApplicationConfig;
import ru.yandex.passport.tvmauth.TvmClient;
import ru.yandex.taxi.conversation.common.lock.yt.LockConfiguration;
import ru.yandex.taxi.conversation.common.lock.yt.LockRegistry;
import ru.yandex.taxi.conversation.common.lock.yt.YtConfiguration;
import ru.yandex.taxi.conversation.common.yav.YavClient;
import ru.yandex.taxi.conversation.common.yav.YavConfiguration;
import ru.yandex.taxi.conversation.logbroker.LogbrokerService;
import ru.yandex.taxi.conversation.logbroker.read.LogbrokerReader;
import ru.yandex.taxi.conversation.mds.MdsService;
import ru.yandex.taxi.conversation.utils.ObjectMapperConfiguration;

@SpringBootTest(
        classes = {SpringApplicationConfig.class, ObjectMapperConfiguration.class},
        webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT
)
@Import(AbstractFunctionalTest.FunctionalTestConfiguration.class)
public abstract class AbstractFunctionalTest {

    @TestConfiguration
    static class FunctionalTestConfiguration {

        @MockBean
        private LockConfiguration lockConfiguration;

        @MockBean
        private YavConfiguration yavConfiguration;

        @MockBean
        private YtConfiguration ytConfiguration;

        @MockBean
        private LockRegistry lockRegistry;

        @MockBean
        private YavClient yavClient;

        @MockBean
        private MdsS3Client mdsS3Client;

        @MockBean
        private MdsService mdsService;

        @MockBean
        private LogbrokerReader logbrokerReader;

        @MockBean
        private LogbrokerService logbrokerService;

        @MockBean
        private TvmClient tvmClient;
    }
}
