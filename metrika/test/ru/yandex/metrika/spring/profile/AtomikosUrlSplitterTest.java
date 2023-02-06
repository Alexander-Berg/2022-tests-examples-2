package ru.yandex.metrika.spring.profile;

import org.junit.Test;

import static org.assertj.core.api.AssertionsForClassTypes.assertThat;

public class AtomikosUrlSplitterTest {

    @Test
    public void postgreUrl() {
        DatasourceUrlSplitter atomikosUrlSplitter = new DatasourceUrlSplitter("jdbc:postgresql://vla-ye8mlnudbhi1hg6a.db.yandex.net:6432,man-wwhv8gqv44gpuk08.db.yandex.net:6432,sas-a08ya57kn6nuzzr6.db.yandex.net:6432/metrika_affinity_test?loggerLevel=DEBUG&ssl=true&sslfactory=org.postgresql.ssl.NonValidatingFactory&connectTimeout=30&socketTimeout=30&ApplicationName=faced_stasfil-osx&targetServerType=master&loadBalanceHosts=true");
        assertThat(atomikosUrlSplitter.getDatabase()).isEqualTo("metrika_affinity_test");
        assertThat(atomikosUrlSplitter.getHost()).isEqualTo("vla-ye8mlnudbhi1hg6a.db.yandex.net:6432,man-wwhv8gqv44gpuk08.db.yandex.net:6432,sas-a08ya57kn6nuzzr6.db.yandex.net:6432");
    }
}
