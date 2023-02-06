use IO::Handle;

sub do_test {
    chomp(my $task_type = readline(STDIN));

    if ($task_type eq "0") {
        while (chomp(my $message = readline(STDIN))) {
            if ($message eq "") {
                last;
            }
            print("Message from perl: ".$message."\n");
        }
        print "\n";
    } elsif ($task_type eq "1") {
        chomp(my $empty_line = readline(STDIN));
        if ($empty_line ne "") {
            die "Expected empty line";
        }

        print("Hello\n");
        sleep(5);
        print("world\n");
        print("\n");
    }

    STDOUT->flush();
}

print("ready\n\n");
STDOUT->flush();

while(1) {
    do_test();
}
