#!/usr/bin/env perl

# perl -d:NYTProf ./init_datas.pl
# nytprofhtml --out ../../nytprof/init_datas

use lib::abs qw(../../lib);
use rules;

use MordaX::Data_load;
use MP::Logit;

for (0..100) {
    dmp $_;
    MordaX::Data_load::init_datas({no_time=>1})
}