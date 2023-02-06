package ru.yandex.autotests.morda.utils.cookie.parsers.my;

import javax.xml.bind.DatatypeConverter;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * User: leonsabr
 * Date: 24.06.12
 * Утилитный класс, содержащий метод для разбора портальной куки my.
 * Разбор осуществляется согласно алгоритму http://wiki.yandex-team.ru/MyCookie
 */
public class MyCookieParser {
    /*
     * Закрытый конструктор, так как класс не предназначен для инстанцирования или наследования.
     */
    private MyCookieParser() {
    }

    /**
     * Метод, декодирующий куку my и разбирающий ее на блоки.
     * Если кука -- пустая строка, то возвращается пустая мапа.
     *
     * @param my -- кука, подлежащая разбору на блоки
     * @return map с парами {id блока, список параметров}
     * @throws NullPointerException     если аргумент null
     * @throws IllegalArgumentException если первый байт куки не 0x63
     */
    public static Map<String, List<String>> parse(String my) {
        if (my == null) {
            throw new NullPointerException("Cookie my can't be null!");
        }

        Map<String, List<String>> blocks = new HashMap<String, List<String>>();

        if (my.isEmpty()) {
            return blocks;
        }

        byte[] decoded = DatatypeConverter.parseBase64Binary(my);

        int[] data = new int[decoded.length];

        // byte со знаком преобразуются в беззнаковый int
        for (int i = 0; i < decoded.length; i++) {
            data[i] = decoded[i] & 0xff;
        }

        if (data[0] != 0x63) {
            throw new IllegalArgumentException("Cookie my is invalid: " + my);
        }

        int i = 1;
        while (i < data.length) {
            if (data[i] == 0) {
                i++;
                continue;
            }

            int blockId = data[i++];

            int blockParamsCount = data[i++];
            List<String> params = new ArrayList<String>();

            for (int j = 0; j < blockParamsCount; j++) {
                if (data[i] < 128) {
                    params.add(String.valueOf(data[i]));
                    i++;
                    continue;
                }
                if (data[i] < 192) {
                    params.add(String.valueOf(((data[i] & 0x3f) << 8) + data[i + 1]));
                    i += 2;
                    continue;
                }
                if (data[i] < 240) {
                    params.add(String.valueOf(((data[i] & 0xf) << 24) + (data[i + 1] << 16) +
                            (data[i + 2] << 8) + data[i + 3]));
                    i += 4;
                }
            }
            blocks.put(String.valueOf(blockId), params);
        }

        return blocks;
    }
}
