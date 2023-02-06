#include "gtest/gtest.h"

#include "../src/hashtable.h"

namespace
{

TEST(HashtableTest, Basic)
{
	dataplane::hashtable_chain_t<int, int, CONFIG_YADECAP_ACL_TRANSPORT_HT_SIZE, CONFIG_YADECAP_ACL_TRANSPORT_HT_EXTENDED_SIZE, 4, 4> t;

	int* v;
	int k = 1;
	t.lookup(&k, &v, 1);
	EXPECT_EQ(nullptr, v);

	EXPECT_EQ(true, t.insert(1, 1));
	EXPECT_EQ(true, t.insert(1, 1));

	t.lookup(&k, &v, 1);
	EXPECT_EQ(1, *v);

	t.clear();
	t.lookup(&k, &v, 1);
	EXPECT_EQ(nullptr, v);
}

TEST(HashtableTest, Extended)
{
	dataplane::hashtable_chain_spinlock_t<int, int, 128, 128, 2, 4> t;

	for (int k = 0; k < 512; ++k)
	{
		if ((k % 7) && (k % 11))
		{
			t.insert(k, k);
		}
	}

	bool ok = true;

	for (int k = 0; k < 512; ++k)
	{
		int* v;
		dataplane::spinlock_t* locker;

		t.lookup(k, v, locker);
		if ((k % 7) && (k % 11))
		{
			if (v)
			{
				ok &= *v == k;
				locker->unlock();
			}
			else
			{
				ok = false;
				break;
			}
		}
		else
		{
			if (v)
			{
				ok = false;
				break;
			}
		}
	}

	EXPECT_TRUE(ok);
	EXPECT_NE(t.getStats().extendedChunksCount, 0);

	uint32_t from = 0;
	for (auto iter : t.range(from, 8192))
        {
		iter.lock();
		if (iter.isValid())
		{
			int key = *iter.key();
			int value = *iter.value();
			if (key == value &&
			    0 <= value &&
			    value < 512 &&
			    (key % 7) && (key % 11))
			{
				iter.unsetValid();
			}
		}
		iter.gc();
		iter.unlock();
	}

	from = 0;
	for (auto iter : t.range(from, 8192))
        {
		iter.lock();
		iter.gc();
		iter.unlock();
	}

	EXPECT_EQ(t.getStats().extendedChunksCount, 0);
	EXPECT_EQ(t.getStats().pairs, 0);

	for (int k = 0; k < 512; ++k)
	{
		if ((k % 7) && (k % 11))
		{
			t.insert(k, k);
		}
	}

	for (int k = 0; k < 512; ++k)
	{
		if ((k % 7) && (k % 11))
		{
			t.remove(k);
		}
	}

	from = 0;
	for (auto iter : t.range(from, 8192))
        {
		iter.lock();
		iter.gc();
		iter.unlock();
	}

	EXPECT_EQ(t.getStats().extendedChunksCount, 0);
	EXPECT_EQ(t.getStats().pairs, 0);



	for (int k = 0; k < 100500; ++k)
	{
		t.insert(k, k);
	}

	EXPECT_EQ(t.getStats().extendedChunksCount, 128);
	EXPECT_EQ(t.getStats().pairs, 128 * 2 + 128 * 4);

	t.clear();

	EXPECT_EQ(t.getStats().extendedChunksCount, 0);
	EXPECT_EQ(t.getStats().pairs, 0);
}

}
