#! /bin/sh

if [ $# = 0 ] ; then
    echo "usage: make_test.sh <path to test data dir> [<log level>]"
    exit 1
fi

TEST_PATH=$1

if [ $# = 2 ] ; then
    LOG_LEVEL=$2
else
    LOG_LEVEL=debug
fi

if [ ! -e prevdata ] ; then
    mkdir prevdata
fi

if [ ! -e work ] ; then
    mkdir work
fi 

if [ ! -e newdata ] ; then
    mkdir newdata
fi

# mandatory file
datawork load -i $TEST_PATH/work_loghost.dat.txt thostrec > work/loghost.dat

#ext-hosts file
if [ -e $TEST_PATH/new_sitemapexthost.dat.txt ] ; then
    datawork load -i $TEST_PATH/new_sitemapexthost.dat.txt thostrec > newdata/sitemapexthost.dat
else
    rm -f newdata/sitemapexthost.dat
fi

#prev-files
if [ -e $TEST_PATH/prev_sitemapstat.dat.txt ] ; then 
    datawork load -i $TEST_PATH/prev_sitemapstat.dat.txt tsitemapstatrec > prevdata/sitemapstat.dat
else
    rm -f prevdata/sitemapstat.dat
fi

if [ -e $TEST_PATH/prev_sitemapurls.dat.txt ] ; then 
    datawork load -i $TEST_PATH/prev_sitemapurls.dat.txt tsitemapurlsrec > prevdata/sitemapurls.dat
else 
    rm -f prevdata/sitemapurls.dat
fi

if [ -e $TEST_PATH/prev_sitemapowners.dat.txt ] ; then 
    datawork load -i $TEST_PATH/prev_sitemapowners.dat.txt tsitemapownersrec > prevdata/sitemapowners.dat
else 
    rm -f prevdata/sitemapowners.dat
fi

if [ -e $TEST_PATH/prev_sitemaperrs.dat.txt ] ; then 
    datawork load -i $TEST_PATH/prev_sitemaperrs.dat.txt tsitemaperrsrec > prevdata/sitemaperrs.dat
else
    rm -f prevdata/sitemaperrs.dat
fi

#work-files
if [ -e $TEST_PATH/work_robots.dat.txt ] ; then 
    datawork load -i $TEST_PATH/work_robots.dat.txt trobotsrec > work/robots.dat
else 
    rm -f work/robots.dat
fi

if [ -e $TEST_PATH/work_updsitemapurl.dat.txt ] ; then 
    datawork load -i $TEST_PATH/work_updsitemapurl.dat.txt tupdsitemapurlrec > work/updsitemapurl.dat
    datawork load -i $TEST_PATH/work_updsitemapurl.idx.txt urlid_t > work/updsitemapurl.idx
    #./makeindex work/updsitemapurl.dat work/updsitemapurl.idx
else 
    rm -f work/updsitemapurl.dat
    rm -f work/updsitemapurl.idx
fi

if [ -e $TEST_PATH/work_webmastersitemaps.dat.txt ] ; then 
    datawork load -i $TEST_PATH/work_webmastersitemaps.dat.txt twebmastersitemaprec > work/webmastersitemaps.dat
else 
    rm -f work/webmastersitemaps.dat
fi

if [ -e $TEST_PATH/work_sitemapstat.dat.txt ] ; then 
    datawork load -i $TEST_PATH/work_sitemapstat.dat.txt tsitemapstatrec > work/sitemapstat.dat
else
    rm -f work/sitemapstat.dat
fi

if [ -e $TEST_PATH/work_sitemapurls.dat.txt ] ; then 
    datawork load -i $TEST_PATH/work_sitemapurls.dat.txt tsitemapurlsrec > work/sitemapurls.dat
else
    rm -f work/sitemapurls.dat
fi

if [ -e $TEST_PATH/work_sitemapowners.dat.txt ] ; then 
    datawork load -i $TEST_PATH/work_sitemapowners.dat.txt tsitemapownersrec > work/sitemapowners.dat
else
    rm -f work/sitemapowners.dat
fi

if [ -e $TEST_PATH/work_sitemaperrs.dat.txt ] ; then 
    datawork load -i $TEST_PATH/work_sitemaperrs.dat.txt tsitemaperrsrec > work/sitemaperrs.dat
else 
    rm -f work/sitemaperrs.dat
fi

#run it
./dbmerge -h . updsitemap -l $LOG_LEVEL -s 0

# test results 

echo "diff newdata/sitemapstat.dat:"

if [ -e $TEST_PATH/new_sitemapstat.dat.txt ] ; then 
    datawork dump -i newdata/sitemapstat.dat > tmp
    diff $TEST_PATH/new_sitemapstat.dat.txt tmp
else
    datawork dump -i newdata/sitemapstat.dat
fi

echo "diff newdata/sitemapurls.dat:"

if [ -e $TEST_PATH/new_sitemapurls.dat.txt ] ; then 
    datawork dump -i newdata/sitemapurls.dat > tmp
    diff $TEST_PATH/new_sitemapurls.dat.txt tmp
else
    datawork dump -i newdata/sitemapurls.dat
fi

echo "diff newdata/sitemapowners.dat:"

if [ -e $TEST_PATH/new_sitemapowners.dat.txt ] ; then 
    datawork dump -i newdata/sitemapowners.dat > tmp
    diff $TEST_PATH/new_sitemapowners.dat.txt tmp
else
    datawork dump -i newdata/sitemapowners.dat
fi

echo "diff newdata/sitemaperrs.dat:"

if [ -e $TEST_PATH/new_sitemaperrs.dat.txt ] ; then 
    datawork dump -i newdata/sitemaperrs.dat > tmp
    diff $TEST_PATH/new_sitemaperrs.dat.txt tmp
else
    datawork dump -i newdata/sitemaperrs.dat
fi

rm tmp

