#!/usr/bin/perl

use Test::More qw(no_plan);

use common;
use strict;
use warnings;

use lib::abs qw( ../scripts/ );
require 'widgets_job.pl';

#use POSIX;
use WADM::Conf;

use Jobs::statistic_updater;
use starter;
starter::init_wadm();

ok(WADM::Conf->get('StatsMaster'), "db info found ");
ok(
    Jobs::statistic_updater::save_target_function_stats({
            date             => '2010-10-01',
            full             => 0,
            full_no_users    => 0.1,
            cr               => 1,
            cr_no_users      => 1.1,
            cr_only          => 2,
            cr_only_no_users => 2.1,
            c_only           => 3,
            c_only_no_users  => 3.1,
            r_only           => 4,
            r_only_no_users  => 4.1,

        }
    ),
    'stats updated'
);

