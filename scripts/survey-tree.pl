#!/usr/bin/env perl
use strict;
use warnings;
use utf8;
use File::Find;
use File::Path qw(make_path);
use FindBin;

my $ROOT = "$FindBin::Bin/..";

my $SOURCE_ROOT = "$ROOT/SRYSO-Student-Folders";
my $LOG_DIR     = "$ROOT/logs";
my $OUT         = "$LOG_DIR/sryso-tree-survey.txt";

make_path($LOG_DIR);

my @ignore_dir_patterns = (
    qr/seating/i,
    qr/recording/i,
    qr/master-docs/i,
);

my @semester_dirs;

opendir(my $dh, $SOURCE_ROOT) or die "Cannot open $SOURCE_ROOT: $!";
while (my $entry = readdir($dh)) {
    next if $entry =~ /^\./;
    my $path = "$SOURCE_ROOT/$entry";
    next unless -d $path;
    next if grep { $entry =~ $_ } @ignore_dir_patterns;
    push @semester_dirs, $entry;
}
closedir($dh);

@semester_dirs = sort @semester_dirs;

open my $out, ">:encoding(UTF-8)", $OUT or die "Cannot write $OUT: $!";

print $out "SRYSO TREE SURVEY\n";
print $out "Source root: $SOURCE_ROOT\n\n";

for my $semester (@semester_dirs) {
    my $semester_path = "$SOURCE_ROOT/$semester";

    print $out "=== $semester ===\n";

    opendir(my $sdh, $semester_path) or do {
        print $out "  [cannot open]\n\n";
        next;
    };

    my @entries;
    while (my $entry = readdir($sdh)) {
        next if $entry =~ /^\./;
        my $path = "$semester_path/$entry";
        next unless -d $path;

        my $ignore = grep { $entry =~ $_ } @ignore_dir_patterns;

        push @entries, {
            name   => $entry,
            path   => $path,
            ignore => $ignore,
        };
    }
    closedir($sdh);

    for my $dir (sort { $a->{name} cmp $b->{name} } @entries) {
        my $tag = $dir->{ignore} ? "[IGNORED]" : "[CANDIDATE]";
        my ($pdf_count, $mscz_count, $subdir_count) = count_music_assets($dir->{path});

        printf $out "  %s %s\n", $tag, $dir->{name};
        printf $out "      PDFs: %d | MSCZ: %d | Subdirs: %d\n",
            $pdf_count, $mscz_count, $subdir_count;

        my @subdirs = immediate_subdirs($dir->{path});
        for my $sub (@subdirs) {
            my $subtag = ($sub =~ /old|ignore|do[-_ ]?not[-_ ]?use/i) ? "[skip?]" : "[subdir]";
            print $out "        $subtag $sub\n";
        }
    }

    print $out "\n";
}

close $out;

print "Wrote $OUT\n";

sub immediate_subdirs {
    my ($dir) = @_;
    opendir(my $dh, $dir) or return;
    my @subs;
    while (my $entry = readdir($dh)) {
        next if $entry =~ /^\./;
        push @subs, $entry if -d "$dir/$entry";
    }
    closedir($dh);
    return sort @subs;
}

sub count_music_assets {
    my ($dir) = @_;

    my ($pdf, $mscz, $subdirs) = (0, 0, 0);

    find({
        wanted => sub {
            return if $_ =~ /^\./;

            if (-d $File::Find::name) {
                $subdirs++ unless $File::Find::name eq $dir;
                return;
            }

            $pdf++  if /\.pdf$/i;
            $mscz++ if /\.mscz$/i;
        },
        no_chdir => 1,
    }, $dir);

    return ($pdf, $mscz, $subdirs);
}
