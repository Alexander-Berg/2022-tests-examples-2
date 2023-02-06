import java.net.InetAddress;
import java.net.UnknownHostException;

public class TAXIDWH_4595_Test {
    public static void main(String[] args) throws UnknownHostException, InterruptedException {
        System.out.println(System.getProperty("java.net.preferIPv4Stack"));
        System.out.println(System.getProperty("user.name"));
        System.out.println(InetAddress.getByName("sas4-1500-node-hahn.sas.yp-c.yandex.net"));
    }
}
