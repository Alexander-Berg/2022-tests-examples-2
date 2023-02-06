package ru.yandex.autotests.mordabackend.beans.blocks;

import java.util.List;

import ch.lambdaj.Lambda;
import com.fasterxml.jackson.annotation.JsonCreator;

/**
 * User: ivannik
 * Date: 04.12.2014
 */
public class Blocks {

    private List<List<String>> blockLists;

    @JsonCreator
    public Blocks(List<List<String>> blockLists) {
        this.blockLists = blockLists;
    }

    public List<List<String>> getBlockLists() {
        return blockLists;
    }

    public List<String> getFlattenBlockList() {
        return Lambda.flatten(blockLists);
    }

    @Override
    public String toString() {
        return "Blocks" + blockLists;
    }
}
