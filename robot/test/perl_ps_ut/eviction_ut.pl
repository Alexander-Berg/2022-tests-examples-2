print("ready\n\n");
STDOUT->flush();

my $i = 0;
while (1) {
    print($i."\n\n");
    STDOUT->flush();
    $i = $i + 1;
    sleep(1);
}
