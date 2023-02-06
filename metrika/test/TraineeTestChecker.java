import java.net.InetAddress;
import java.util.Scanner;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import org.junit.Ignore;

import static org.junit.Assert.assertEquals;

/**
 * тут мы будем проверять креативы
 * @author orantius
 * @version $Id$
 * @since 4/9/13
 */

@SuppressWarnings("ClassWithoutPackageStatement")
@Ignore
public class TraineeTestChecker {

    public static void main(String[] args) {

        byte n =  0xc0^0xff ;
        System.out.println( Long.toBinaryString(n)); // binary printout
        System.out.println( n); //decimal printout
        //checkRegExp();
        //checkIP();
    }

    public static String ip(int value) {
            // Результат
            String result = "";
        // Бинарная строка
            String binaryString;
        // Бинарная строка восьми мит
            String eightBitString;
            // Восми битовой int
            int eightBitInt;
            // Длина двоичной строки из десятичной
            int len;
            // Получаем двоичную строку из десятичного числа
            binaryString = java.lang.Integer.toBinaryString(value);
            len = binaryString.length();
            //System.out.print(str.length());
            // Добавляем до длины 32 бита
            for (int i=0;i < 32-len;i++) {
                binaryString = '0' + binaryString;
            }
            // Обрабатываем по 8 бит., формируем IP
            for (int i=0; i < 4; i++)
            {
                    eightBitString = binaryString.substring(i*8,(i+1)*8);
                    // По восьми битам получаем Int
                    eightBitInt = Integer.parseInt(eightBitString,2);
                    result += String.valueOf(eightBitInt) + '.';
            }
            // Убираем последнюю точку
            result = result.substring(0,result.length()-1);
            return result;
    }


    private static void checkIP() {
        assertEquals("255.255.255.255", ip2String(-1));
        assertEquals("255.255.255.254", ip2String(-2));
        assertEquals("0.0.0.0", ip2String(0));
        assertEquals("0.0.0.1", ip2String(1));
        assertEquals("0.0.0.2", ip2String(2));
    }

    private static void checkRegExp() {
        char[] chars = {'a', 'A', 'S', 'Ы', '.', '-','#'};
        assertEquals(false, check(""));
        assertEquals(true, check("a"));
        assertEquals(true, check("A"));
        assertEquals(false, check("0"));
        assertEquals(true, check("S"));
        assertEquals(false, check("Ы"));
        assertEquals(false, check("\\"));
        assertEquals(false, check("1"));
        assertEquals(false, check("."));
        assertEquals(false, check("-"));
        assertEquals(false, check("#"));

        assertEquals(true, check("aa"));
        assertEquals(true, check("aA"));
        assertEquals(true, check("aS"));
        assertEquals(false, check("aЫ"));
        assertEquals(true, check("a1"));
        assertEquals(false, check("a."));
        assertEquals(false, check("a-"));
        assertEquals(false, check("a#"));

        assertEquals(true, check("aaa"));
        assertEquals(true, check("aaA"));
        assertEquals(true, check("aaS"));
        assertEquals(false, check("aaЫ"));
        assertEquals(false, check("aa\\"));
        assertEquals(true, check("aa1"));
        assertEquals(false, check("aa."));
        assertEquals(false, check("aa-"));
        assertEquals(false, check("aa#"));

        assertEquals(true, check("a-a"));
        assertEquals(true, check("a-A"));
        assertEquals(true, check("a-S"));
        assertEquals(false, check("a-Ы"));
        assertEquals(false, check("a-\\"));
        assertEquals(true, check("a-1"));
        assertEquals(false, check("a-."));
        assertEquals(false, check("a--"));
        assertEquals(false, check("a-#"));

        assertEquals(true, check("a.a"));
        assertEquals(true, check("a.A"));
        assertEquals(true, check("a.S"));
        assertEquals(false, check("a.Ы"));
        assertEquals(false, check("a.\\"));
        assertEquals(true, check("a.1"));
        assertEquals(false, check("a.."));
        assertEquals(false, check("a.-"));
        assertEquals(false, check("a.#"));

        assertEquals(false, check("aыa"));
        assertEquals(false, check("a\\a"));
        assertEquals(false, check("aыA"));
        assertEquals(false, check("aыS"));
        assertEquals(false, check("aыЫ"));
        assertEquals(false, check("a\\Ы"));
        assertEquals(false, check("aы\\"));
        assertEquals(false, check("a\\\\"));
        assertEquals(false, check("aы1"));
        assertEquals(false, check("a\\1"));
        assertEquals(false, check("aы."));
        assertEquals(false, check("aы-"));
        assertEquals(false, check("aы#"));

        assertEquals(true, check("abcdefghijabcdefghij"));
        assertEquals(false, check("abcdefghijabcdefghij0"));
        assertEquals(false, check("abcdefghijabcdefghij."));
        assertEquals(false, check("abcdefghijabcdefghij-"));

        assertEquals(true, check("abcdefghijabcdefghi0"));
        assertEquals(false, check("abcdefghijabcdefghi."));
        assertEquals(false, check("abcdefghijabcdefghi-"));
        assertEquals(false, check("abcdefghijabcdefghiЫ"));

        assertEquals(true, check("abcdefghijabcdefgh0"));
        assertEquals(false, check("abcdefghijabcdefgh."));
        assertEquals(false, check("abcdefghijabcdefgh-"));
        assertEquals(false, check("abcdefghijabcdefghЫ"));

        assertEquals(true, check("abc--------def"));
        assertEquals(true, check("abc........def"));
        assertEquals(true, check("abc-.-.-.-.def"));
        assertEquals(true, check("abc.-.-.-.-def"));

    }

    public static boolean method3( String a) {
        if((a.length()<1)||(a.length()>20))
            return false;
        char c=a.charAt(0);
        if(c<'A'||c>'z')
            return false;
        for( int i=1;i< a.length()-1;i++) {
                c=a.charAt(i);
                if(c<'A'||c>'z')
                {
                 if(c<'0'||c>'9')
                     if(c!='.'&&c!='-')
                         return false;
                }

        }
        c=a.charAt(a.length()-1);
        return !((c < 'A' || c > 'z') && (c < '0' || c > '9'));
    }
    private static boolean check(String login) {
        String regexp = "(^[a-zA-Z][a-zA-Z0-9\\.-]{0,18}[a-zA-Z0-9]$)|(^[a-zA-Z]$)";
        return Pattern.compile(regexp).matcher(login).matches();

        //return method3(login);
        /*String regexp = "([a-z||A-Z]){1}(([a-z||A-Z||0-9||/.||/-]){0,18}([a-z||A-Z||0-9]){1}){0,19}";
        return Pattern.compile(regexp).matcher(login).matches();*/
        //String regexp = "[a-zA-Z]+|([a-zA-Z]+[a-zA-Z0-9\\.-]+[a-zA-Z0-9]+)";
        /*while ( ! ( ! login.isEmpty ( ) &&
                            (login.length ( ) < 21) &&
                            login.matches ( "[A-Za-z0-9.-]+" ) &&
                            Character.isLetter ( login.charAt ( 0 ) ) &&
                            Character.isLetterOrDigit ( login.charAt ( login.length( ) - 1 ) ) ) ) {
            return false;
        }
        return true;*/
        //return Pattern.compile("^[a-zA-Z][-a-zA-Z0-9\\.]{1,18}[a-zA-Z0-9]$").matcher(login).matches();
        /*boolean checkFlag;
        char c[] = login.toCharArray();
        int i;
        checkFlag = true;
        for (i = 0; i < login.length(); i++) {
            if ((c[i] >= 'A' && c[i] <= 'Z') || (c[i] >= 'a' && c[i] <= 'z')) {
            } else {
                if (i != 0 && (c[i] >= '0' && c[i] <= '9')) {
                } else {
                    if (i != 0 && i != (login.length() - 1) && (c[i] == '.' || c[i] == '-')) {
                    } else {
                        System.out.println("Uncorrect login");
                        checkFlag = false;
                        break;
                    }

                }
            }
            //System.out.println((int)c[i]);
        }
        if (checkFlag == true) {
            System.out.println("Login correct");
        }
        return checkFlag; */
        /*Pattern p1 = Pattern.compile("(^[a-zA-Z][a-zA-Z0-9.-]{0,18}[a-zA-Z0-9]$)");
        Pattern p2 = Pattern.compile("([a-zA-Z])");
        Pattern p3 = Pattern.compile("[a-zA-Z0-9]");
        Matcher m1 = p1.matcher(login);
        Matcher m2 = p2.matcher(login);
        Matcher m3 = p3.matcher(login);
        return m1.matches()||m2.matches()||m3.matches(); */

        /*return login.length() > 0 &&
               login.length() <= 20 &&
               login.matches("^[a-zA-Z](?!(.*\\.){2})[a-zA-Z0-9]*(?!(.*\\-){2})(?!(.*\\.$))(?!(.*\\-$))(?=[a-zA-Z0-9.-]*).*");*/

        /*Pattern expression1 = Pattern.compile("([A-z]{1}[a-zA-Z\\d\\.\\-]{0,18}[a-zA-Z])");
              Pattern expression2 = Pattern.compile("([A-z]{1})");
        return expression1.matcher(login).matches()||expression2.matcher(login).matches();*/
        // return login.matches("(^[a-zA-Z][a-zA-Z0-9\\.-]{0,18}[a-zA-Z0-9]$)|(^[a-zA-Z]{1,20}$)");
        // (^[a-zA-Z][a-zA-Z0-9\\.-]{0,18}[a-zA-Z0-9]$)|(^[a-zA-Z]{1,20}$)
        // return login.matches("((?=.*\\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[.-]).{1,20})");

        //return login.matches("^[A-Za-z]{1}[A-Za-z0-9-/.]{0,18}[A-Za-z0-9]{1}$|^[A-Za-z]{1}$");
        //return login.matches("^[a-zA-Z](([-\\.a-zA-Z0-9])*([a-zA-Z]|[0-9])){0,19}$");
        // return login.matches("^[a-z,A-Z][a-z,A-Z,0-9,\\.,\\-]{0,18}[a-z,A-Z,0-9]+?$");

        /*Pattern p1 = Pattern.compile("([a-zA-Z]{1}[a-zA-Z\\d.-]{0,18}[a-zA-Z\\d])");
        Pattern p2 = Pattern.compile("([a-zA-Z]{1})");
        Matcher m1 = p1.matcher(login);
        Matcher m2 = p2.matcher(login);
        return m1.matches()||m2.matches(); */
/*
                  // Ограничения на длину
          if ((login.length() < 1) || (login.length() > 20))
                  return false;
          // Если у нас только один символ, то он должен быть буквенным
          if (login.length() == 1)
                  return login.matches("^[a-zA-Z]$");
          return login.matches("^[a-zA-Z][a-zA-Z\\.\\-0-9]*[a-zA-Z0-9]$");*/

        // return login.matches("^\\p{Alpha}[[-\\.\\w]&&[^_]]+[\\w&&[^_]]$");

/*
        if (login.isEmpty() || login.length()>20) { return false; }
            Pattern patt1 = Pattern
                       .compile("^[a-zA-Z](([a-zA-Z\\d]*\\.?[a-zA-Z\\d]*-?[a-zA-Z\\d]*|[a-zA-Z\\d]*-?[a-zA-Z\\d]*\\.?[a-zA-Z\\d]*)[a-zA-Z0-9])?$");
            Matcher mat1 = patt1.matcher(login);
            return mat1.matches();*/
    }


    public static void main2(String[] args) throws Exception{
        String s = InetAddress.getByName("2130706433").toString();
        System.out.println("s = " + s);
        System.out.println("s = " + Integer.toHexString(2130706433));

        System.out.println("integerIPtoString = " + integerIPtoString(2130706433));

    }

    public static String reg() {
            Scanner input = new Scanner(System.in);
            String str = input.next();
            Pattern pattern = Pattern
                    .compile("\\b[a-zA-Z]([\\w . -]){0,18}(\\w\\b)?");
            Matcher mat = pattern.matcher(str);
            boolean flag = mat.matches();
        System.out.println("flag = " + flag);
        return "";
    }
    public static String integerIPtoString(int ip) {
        final int mask = 0xFF;

        StringBuilder sb = new StringBuilder();

        sb.append(ip >> 8 * 3 & mask).append('.');
        sb.append(ip >> 8 * 2 & mask).append('.');
        sb.append(ip >> 8 * 1 & mask).append('.');
        sb.append(ip & mask);

        return sb.toString();
    }

    public static String ip2String(long ip){
            StringBuilder sb=new StringBuilder();
            for(int i=3; i>=0; i--){
                int x= (int) (ip>>i*8&0xff);
                sb.append(x).append(".");
            }
            return sb.toString().substring(0, sb.length()-1);
    }

    @SuppressWarnings("PointlessBitwiseExpression")
    private static String ipIntToString(int ip) {
            return String.valueOf((byte)  (ip >> 24)) + '.' +
                    String.valueOf((byte) (ip >> 16)) + '.' +
                    String.valueOf((byte) (ip >> 8)) + '.' +
                    String.valueOf((byte) (ip >> 0));
        }

    public static String ipNumToString(int ip) {
        long uIp = (long)ip + (long)Integer.MAX_VALUE + 1;
        long div;
        div = uIp/ 256L / 256L / 256L;
        String s = div + ".";
        uIp -= div* 256L * 256L * 256L;
        div = uIp/ 256L / 256L;
        s += div + ".";
        uIp -= div* 256L * 256L;
        div = uIp/ 256L;
        s += div + ".";
        uIp -= div* 256L;
        div = uIp;
        s += div;
        return s;
    }
    public static void main3 (String[] args) {
        System.out.println("args = " + ipNumToString(Integer.parseInt("-33333333",16))+ ' ' + Integer.toHexString(2130706433));

    String login = "Peter-2.05.90-1User";
    if (login.length() < 1 || login.length() > 20) {
    System.out.println("Логин должен содержать не менее одного, и не более 20 символов");
    System.exit(-1);
    }
    boolean agreement =  Pattern.matches("[a-zA-Z](([a-zA-Z0-9-.]){0,18}[a-zA-Z0-9])?", login);
    if (!agreement) {
    System.out.println("Исплозованы запрещённые символы");
    System.out.println("Логин должен начинаться и заканчиваться с латинской буквы, может состоять из латинских букв, цифр, точки и минуса");
    System.exit(-1);
    } else {
    System.out.println("Логин успешно прошёл проверку");
    }

    }

    public static void main4(String[] args) throws Exception {
        String s = ipNumToString(0x01020304);
        System.out.println("s = " + s);
    }
}
