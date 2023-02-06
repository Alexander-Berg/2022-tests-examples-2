package ru.yandex.metrika.storage.merger.impl;

import java.io.DataInputStream;
import java.io.IOException;
import java.util.Date;

/**
 *
* Created by orantius on 4/12/14.
*/

class StoredEntity {
    final int counterId;
    final long visitId;
    final long time;
    String content;

    public int getCounterId() {
        return counterId;
    }

    public long getVisitId() {
        return visitId;
    }

    StoredEntity(DataInputStream in) throws IOException {
        counterId = in.readInt();
        visitId = in.readLong();
        time = in.readLong();
        content = in.readUTF();
    }

    StoredEntity(int counterId, long visitId, Date date, String content) {
        this.counterId = counterId;
        this.visitId = visitId;
        this.time = date.getTime();
        this.content = content;
    }

    @Override
    public String toString() {
        final StringBuilder sb = new StringBuilder();
        sb.append("TestEntity");
        sb.append("{counterId=").append(counterId);
        sb.append(", visitId=").append(visitId);
        sb.append(", time=").append(time);
        sb.append(", content='").append(content).append('\'');
        sb.append('}');
        return sb.toString();
    }
}
