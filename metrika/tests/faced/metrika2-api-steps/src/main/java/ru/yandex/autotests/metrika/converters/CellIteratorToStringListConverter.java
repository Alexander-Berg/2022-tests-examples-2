package ru.yandex.autotests.metrika.converters;

import org.apache.commons.lang3.StringUtils;
import org.apache.poi.ss.usermodel.Cell;

import java.util.Iterator;
import java.util.List;
import java.util.Objects;
import java.util.function.Function;
import java.util.stream.StreamSupport;

import static java.util.stream.Collectors.toList;

/**
 * Created by konkov on 16.04.2015.
 */
public class CellIteratorToStringListConverter implements Function<Iterator<Cell>, List<String>> {

    @Override
    public List<String> apply(Iterator<Cell> cellIterator) {
        Iterable<Cell> iterable = () -> cellIterator;

        return StreamSupport
                .stream(iterable.spliterator(), false)
                .map(cell -> {
                    switch (cell.getCellType()) {
                        case Cell.CELL_TYPE_STRING:
                            return cell.getRichStringCellValue().getString();
                        case Cell.CELL_TYPE_NUMERIC:
                            return Objects.toString(cell.getNumericCellValue());
                        default:
                            return StringUtils.EMPTY;
                    }
                }).collect(toList());
    }

    public static CellIteratorToStringListConverter cellToStringList() {
        return new CellIteratorToStringListConverter();
    }
}
