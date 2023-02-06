package ru.yandex.autotests.internalapid.properties;

import ru.yandex.autotests.metrika.commons.vault.VaultClient;
import ru.yandex.qatools.properties.PropertyLoader;
import ru.yandex.qatools.properties.annotations.Property;
import ru.yandex.qatools.properties.annotations.Resource;

@Resource.Classpath("mysql.properties")
public class MySqlProperties {

    private static final MySqlProperties INSTANCE = new MySqlProperties();

    private MySqlProperties() {
        PropertyLoader.populate(this);
    }

    public static MySqlProperties getInstance() {
        return INSTANCE;
    }

    @Property("mysql.host")
    private String host;

    @Property("mysql.port")
    private int port;

    @Property("mysql.user")
    private String user;

    @Property("mysql.password")
    private String password;

    @Property("mysql.rbacDb")
    private String rbacDb;

    @Property("mysql.countersDb")
    private String countersDb;

    public String getHost() {
        return host;
    }

    public int getPort() {
        return port;
    }

    public String getUser() {
        return user;
    }

    public String getPassword() {
        if (password.startsWith("from-yav:")) {
            String[] split = password.substring(9).split("/");
            password = VaultClient.loadLastVersion(split[0]).get(split[1]);
        }
        return password;
    }

    public String getRbacDb() {
        return rbacDb;
    }

    public String getCountersDb() {
        return countersDb;
    }
}
