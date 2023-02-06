#!/usr/local/bin/bash

set -xue -o pipefail -o posix

export PATH=/bin:/usr/bin:/usr/local/bin:$1/bin:$1/bin/scripts

home=$1
log_path=$2

host=`python -c 'import socket; print socket.gethostbyaddr(socket.gethostname())[0]'`

mainurl_info="$home/mainurl.info"
test_urls="$home/urls.in_base"
gemini_data="$home/data"
gemini_config="$home/config"

basedir="$home/BASE"
points="$home/points"

castor_port=20000
castor_monport=21000

tab=$(printf '\t')

function prepare_index() {
    local home=$1
    local weak=$home/weak.index
    local strong=$home/strong.index
    local ncweak=$home/nc.weak.index
    local ncstrong=$home/nc.strong.index

    sort -u $weak -o $weak.nondup
    sort -u $strong -o $strong.nondup
     
    comm -12 $weak.nondup $strong.nondup > $home/common.index
    comm -23 $weak.nondup $strong.nondup > $ncweak
    comm -13 $weak.nondup $strong.nondup > $ncstrong
}

# generate squota.gemini.xml file
printf "\
<ipset name=\"all\">\n\
  <ip name=\"*\"/>\n\
</ipset>\n\
<source name=\"any\">\n\
  <requesttype name=\"GetMain\" second=\"10000000\">\n\
    <ipset name=\"all\"/>\n\
  </requesttype>\n\
</source> " >  $gemini_config/squota.gemini.xml

# generate gemini.cfg and points files
printf "\
<Machines>
    BasesPerMachine: 1
    <$host>
        Dc: 0
        <Castor>
            Port: default
        </Castor>
        <Pollux>
            Port: default
        </Pollux>
    </$host>
</Machines>
<DistributedQuotas>\n\
    MTU 8000\n\
    WaitRawStatsTimeout 2\n\
    PrecalcStatsGenerationRate 2\n\
    RawStatsSendingPeriodicity 1\n\
</DistributedQuotas>\n\n\
<Paths>\n\
    mirrors : $gemini_data/mirrors.trie\n\
    mirrors_test : $gemini_data/test.mirrors.trie\n\
    mirrors_new : $gemini_data/new.mirrors.trie\n\
    points : $points\n\
    index : $basedir\n\
    rfl : $gemini_data/filter.rfl\n\
    robotsrfl : $gemini_data/filter.robots.rfl\n\
    areas : $gemini_config/areas.lst\n\
    squota : $gemini_config/squota.gemini.xml\n\
    video_re : $gemini_data/video.re\n\
    video_tmpl : $gemini_data/video.tmpl\n\
    polytrie : $gemini_data/poly.trie
</Paths>" > $gemini_config/gemini.cfg

gemini_lookup -c $gemini_config/gemini.cfg -m CreatePoints -o $points

# prepare data
filter_rfl_timestamp=$(stat -c %Y $gemini_data/filter.rfl)
mirrors_timestamp=$(stat -c %Y $gemini_data/mirrors.trie)
printf "mirrors: %s\nrfl: %s\n" $mirrors_timestamp $filter_rfl_timestamp > $gemini_config/base.info

# create new DB in local MapReduce
rm -rf $basedir
rm -rf $home/temp

mkdir $basedir
mkdir $basedir/0
mkdir $basedir/0/new
mkdir $basedir/0/cur
mkdir $home/temp

# create map
gemini_lookup -m UsePoints -h $host -i $points -o $basedir/hash.map

cat $mainurl_info | create_index_test -m web -f $gemini_data/filter.rfl -r $gemini_data/filter.robots.rfl -d $basedir/0/new
mv $basedir/0/new/weak_hash_2_main_url $basedir/0/new/weak.index
mv $basedir/0/new/strong_hash_2_main_url $basedir/0/new/strong.index

# prepare index
prepare_index $basedir/0/new


gemini_indexer -i $basedir/0/new/nc.weak.index -h $basedir/0/new/weak.hosts.index -o $basedir/0/new/weak.paths.index -m $basedir/0/new/weak.mapped.index
gemini_indexer -i $basedir/0/new/nc.strong.index -h $basedir/0/new/strong.hosts.index -o $basedir/0/new/strong.paths.index -m $basedir/0/new/strong.mapped.index

gemini_indexer -i $basedir/0/new/common.index -h $basedir/0/new/common.hosts.index -o $basedir/0/new/common.paths.index -m $basedir/0/new/common.mapped.index

index_timestamp=$(date +%s)
printf "index: %s\n" $index_timestamp >> $gemini_config/base.info

cp $gemini_config/base.info $basedir/0/new/


# move index files
find $basedir/0/cur/ -mindepth 1 -maxdepth 1 | xargs rm -f
find $basedir/0/new/ -mindepth 1 -maxdepth 1 | xargs -I % mv % $basedir/0/cur/


# start pollux
rm -rf $home/logs
mkdir $home/logs

gemini_pollux \
    -c $home/config/gemini.cfg \
    --verbose-main \
    -w 12 \
    -f $basedir/pollux_started.flag \
    -h $host \
    --max-in-fl 10000 \
    --no-daemon \
    -l 2> $home/logs/pollux.error.log > $home/logs/pollux.log &
echo $! > $basedir/pollux.pid

while [ ! -f $basedir/pollux_started.flag ]; do
    sleep 5
done

# start castor
cd /
gemini_castor \
    -c $gemini_config/gemini.cfg \
    --verbose-main \
    -w 12 \
    -f $basedir/castor_started.flag \
    -p $castor_port \
    -h $host \
    --mon-port $castor_monport \
    --mcast-port 25000 \
    --max-in-fl 50000 \
    --no-daemon \
    -l 2> $home/logs/castor.1.error.log > $home/logs/castor.1.log &
echo $! > $basedir/castor.pid

while [ ! -f $basedir/castor_started.flag ]; do
    sleep 5
done

# run client
/usr/bin/time -p -o $log_path/gemini_time.log  geminicl -h $host -p $castor_port -f $test_urls --quota 10000000 > $home/out.log 2> $home/err.log

sleep 20

kill -15 $(cat $basedir/pollux.pid)
kill -15 $(cat $basedir/castor.pid)

echo "All done!"

