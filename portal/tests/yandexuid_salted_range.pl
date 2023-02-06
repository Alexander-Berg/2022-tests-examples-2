use strict; use warnings;
use Digest::MD5 qw(md5_hex);
use Data::Dumper;
use Digest::SHA1 qw(sha1 sha1_hex sha1_base64);
use String::CRC32;

my $ranges = {};
my $times  = 100000;
my $max    = 1000;
my $normal = $times / $max;
my $slots  = {};

for my $yu_slot (0 .. $times) {

    $yu_slot = int(rand(1000)) . int(rand(1000)) . int(rand(1000));

    my $salt           = '9882llkj';
    my $yu_slot_salted = $yu_slot . ':' . $salt;

=pod
    $yu_slot_salted = crc32($yu_slot_salted);
    $yu_slot_salted = substr($yu_slot_salted, 0, 3); # первые три символа
=cut

=pod 
    $yu_slot_salted = md5_hex($yu_slot_salted);
    $yu_slot_salted = substr($yu_slot_salted, -3);
    $yu_slot_salted = hex '0x'.$yu_slot_salted;
    $yu_slot_salted = substr($yu_slot_salted, -3); 
=cut

=pod
    $yu_slot_salted = md5_hex($yu_slot_salted);
    $yu_slot_salted = substr($yu_slot_salted, -3);
    $yu_slot_salted = join '', (map {substr( hex $_, -1)} split '',$yu_slot_salted);
=cut

    my $bin = Digest::MD5::md5($yu_slot_salted);
    $yu_slot_salted = unpack("I", $bin) % 1000;

    $ranges->{$yu_slot_salted}++;
    #print "\n";
    #$slots->{$yu_slot} = $yu_slot_salted;
}

# общее количество полученных слотов
print "\n\nkeys amount: ";
print scalar(keys %$ranges);
print "\n";

# для всех ключей - сколько раз каждый из них встретился
print "\n\nkey times: \n";
my $amount = 0;
for my $k (sort { int($a) <=> int($b) } keys %$ranges) {
    #print "key: ", $k, "; count: ", $ranges->{$k}," = ".$ranges->{$k} / $normal."\n";
    $amount += $ranges->{$k} / $normal;
}

print "\nAMOUNT: ", $amount;
my $val = {};
for my $v (values %$ranges) {
    $val->{$v}++;
}

# распределение по количеству дубликатов ключей: должно быть около 1
print "\n\nduplicated: \n";
for my $v (sort { int($a) <=> int($b) } keys %$val) {
    print 'times: ' . $v / $normal . '; key amount: ', $val->{$v}, "\n";
}

# ключи, которые вообще не попали в распеределение. теоретически, такое возможно
print "\n\nNOT FOUND: \n";
for my $i (0 .. 999) {
    print "\nnot found " . $i . "\n" if not exists $ranges->{$i};
}
#print Dumper $ranges;
