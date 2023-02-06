package ru.yandex.autotests.metrika.appmetrica.body;

import java.io.File;


/**
 * Тело запроса с типом multipart/form-data, которое в mobmetd используется
 * для передачи файлов. В настоящий момент может содержать только одну часть,
 * которая описывает файл, потому что других способов использования пока нет.
 */
public class MultipartFormBody {

    /**
     * Имя ключа в запросе
     */
    private final String name;
    /**
     * Передаваемый файл
     */
    private final File file;


    public MultipartFormBody(String name, File file) {
        this.name = name;
        this.file = file;
    }

    public String getName() {
        return name;
    }

    public File getFile() {
        return file;
    }
}
