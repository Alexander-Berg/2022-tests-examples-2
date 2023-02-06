package ru.yandex.metrika.util.collections;

import java.util.List;

import org.jetbrains.annotations.NotNull;
import org.junit.Test;

import static junit.framework.Assert.assertEquals;

/**
 * @author Arthur Suilin
 */
public class DoubleLinkedListTest {
  @Test
    public void oneAdd() {
        DoubleLinkedList<Long,DLISimple> target = new DoubleLinkedList<>();
        target.add(new DLISimple(42));
        assertEquals(1, target.getCount());
    }

    @Test
    public void twoAdd() {
        {
            DoubleLinkedList<Long,DLISimple> target = new DoubleLinkedList<>();
            target.add(new DLISimple(42));
            target.add(new DLISimple(43));
            assertEquals(2, target.getCount());
        }
        {
            DoubleLinkedList<Long,DLISimple> target = new DoubleLinkedList<>();
            target.add(new DLISimple(42));
            target.add(new DLISimple(42));
            assertEquals(2, target.getCount());
        }
    }

    @Test
    public void twoAddRemove() {
        {
            DoubleLinkedList<Long,DLISimple> target = new DoubleLinkedList<>();
            DLISimple item = new DLISimple(42);
            target.add(item);
            DLISimple item2 = new DLISimple(43);
            target.add(item2);
            assertEquals(2, target.getCount());
            target.removeItem(item);
            target.removeItem(item2);
            assertEquals(0, target.getCount());
        }
        {
            DoubleLinkedList<Long,DLISimple> target = new DoubleLinkedList<>();
            DLISimple item = new DLISimple(42);
            target.add(item);
            DLISimple item2 = new DLISimple(42);
            target.add(item2);
            assertEquals(2, target.getCount());
            target.removeItem(item);
            target.removeItem(item2);
            assertEquals(0, target.getCount());
        }

        {
            DoubleLinkedList<Long,DLISimple> target = new DoubleLinkedList<>();
            DLISimple item = new DLISimple(42);
            target.add(item);
            assertEquals(1, target.getCount());
            target.removeItem(item);
            assertEquals(0, target.getCount());
            DLISimple item2 = new DLISimple(43);
            target.add(item2);
            assertEquals(1, target.getCount());
            target.removeItem(item2);
            assertEquals(0, target.getCount());
        }
        {
            DoubleLinkedList<Long,DLISimple> target = new DoubleLinkedList<>();
            DLISimple item = new DLISimple(42);
            target.add(item);
            DLISimple item2 = new DLISimple(42);
            target.add(item2);
            assertEquals(2, target.getCount());
            target.removeItem(item);
            assertEquals(1, target.getCount());
            target.removeItem(item2);
            assertEquals(0, target.getCount());
        }

    }

    @Test
    public void testInsertBefore() throws Exception {
        DoubleLinkedList<Long,DLISimple> target = new DoubleLinkedList<>();
        DLISimple elem0 = new DLISimple(42);
        target.add(elem0);
        target.add(new DLISimple(43));
        DLISimple elem2 = new DLISimple(42);
        target.add(elem2);
        target.add(new DLISimple(43));

        DLISimple elem4 = new DLISimple(42);
        target.insertAfter(null, elem2, elem4);
        assertEquals(5, target.getCount());
    }


    @Test
    public void expireTest() {
        {
            DoubleLinkedList<Long,DLISimple> target = new DoubleLinkedList<>();
            target.add(new DLISimple(42));
            target.add(new DLISimple(43));
            target.add(new DLISimple(42));
            target.add(new DLISimple(43));
            target.add(new DLISimple(42));
            assertEquals(5, target.getCount());

            target.expire(new SimpleLinkedList.LinkedListExpirator<DLISimple>() {
                @Override
                public boolean expire(@NotNull DLISimple item) throws Exception {
                    return false;
                }
            }, true);
            assertEquals(5, target.getCount());
            target.expire(new SimpleLinkedList.LinkedListExpirator<DLISimple>() {
                @Override
                public boolean expire(@NotNull DLISimple item) throws Exception {
                    return true;
                }
            }, true);
            assertEquals(0, target.getCount());
        }

        {
            DoubleLinkedList<Long,DLISimple> target = new DoubleLinkedList<>();
            target.add(new DLISimple(42));
            target.add(new DLISimple(43));
            target.add(new DLISimple(42));
            target.add(new DLISimple(43));
            target.add(new DLISimple(42));
            assertEquals(5, target.getCount());

            target.expire(new SimpleLinkedList.LinkedListExpirator<DLISimple>() {
                @Override
                public boolean expire(@NotNull DLISimple item) throws Exception {
                    return item.classId % 2 == 0;
                }
            }, true);
            // возникает вопрос почему этот ассерт работает вот так
            // потому что экспиратор идет с начала списка, пока не произодет false.
            // таким образом, первый элемент уходит, а второй и все остальные остаются.
            assertEquals(4, target.getCount());

        }
    }

    @Test
    public void removeClassTest() {
        {
            DoubleLinkedList<Long,DLISimple> target = new DoubleLinkedList<>();
            target.add(new DLISimple(42));
            target.add(new DLISimple(43));
            target.add(new DLISimple(42));
            target.add(new DLISimple(43));
            target.add(new DLISimple(42));
            assertEquals(5, target.getCount());

            List<DLISimple> res = target.removeClass(42L);
            assertEquals(2, target.getCount());
            assertEquals(3, res.size());
            List<DLISimple> res2 = target.removeClass(43L);
            assertEquals(0, target.getCount());
            assertEquals(2, res2.size());
        }
        {
            DoubleLinkedList<Long,DLISimple> target = new DoubleLinkedList<>();
            target.add(new DLISimple(42));
            target.add(new DLISimple(43));
            target.add(new DLISimple(42));
            target.add(new DLISimple(43));
            target.add(new DLISimple(42));
            assertEquals(5, target.getCount());

            List<DLISimple> res = target.removeClass(43L);
            assertEquals(3, target.getCount());
            assertEquals(2, res.size());
            List<DLISimple> res2 = target.removeClass(42L);
            assertEquals(0, target.getCount());
            assertEquals(3, res2.size());
        }
        {
            DoubleLinkedList<Long,DLISimple> target = new DoubleLinkedList<>();
            target.add(new DLISimple(42));
            assertEquals(1, target.getCount());
            List<DLISimple> res = target.removeClass(100L);
            assertEquals(1, target.getCount());
            assertEquals(res, null);
        }
    }


    static int elemCount;
    static class DLISimple implements DoubleListItem<Long,DLISimple> {
        int id = elemCount++;
        DLISimple next;
        DLISimple previous;
        DLISimple next2;
        DLISimple previous2;

        long classId;

        DLISimple(long classId) {
            this.classId = classId;
        }

        @Override
        public Long getClassId() {
            return classId;
        }

        public DLISimple getNext() {
            return next;
        }

        public void setNext(DLISimple next) {
            this.next = next;
        }

        public DLISimple getPrevious() {
            return previous;
        }

        public void setPrevious(DLISimple previous) {
            this.previous = previous;
        }


        public DLISimple getNext2() {
            return next2;
        }

        public void setNext2(DLISimple next2) {
            this.next2 = next2;
        }

        public DLISimple getPrevious2() {
            return previous2;
        }

        public void setPrevious2(DLISimple previous2) {
            this.previous2 = previous2;
        }

        @Override
        public String toString() {
            return '{' +
                    "id=" + id +
                    ", classId=" + classId +
                    '}';
        }
    }
}
