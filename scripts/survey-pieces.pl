#!/usr/bin/env perl
use strict;
use warnings;
use utf8;
use FindBin;
use File::Path qw(make_path);

my $ROOT        = "$FindBin::Bin/..";
my $SOURCE_ROOT = "$ROOT/SRYSO-Student-Folders";
my $LOG_DIR     = "$ROOT/logs";
my $OUT         = "$LOG_DIR/sryso-piece-inventory.csv";

make_path($LOG_DIR);

my @IGNORE_DIRS = (
    qr/seating/i,
    qr/recording/i,
    qr/master-docs/i,
    qr/^old/i,
    qr/ignore/i,
    qr/do[-_ ]?not[-_ ]?use/i,
    qr/^sryso-scales$/i,
);

my @CONTAINER_DIRS = (
    qr/^ALPHA_/i,
    qr/^OMEGA_/i,
    qr/^PRE-ORCHESTRA/i,
);

open my $out, ">:encoding(UTF-8)", $OUT or die "Cannot write $OUT: $!";

print $out csv_row(qw(
    SEMESTER
    ENSEMBLE-GROUP
    PIECE-DIR
    REL-PATH
    PDF-COUNT
    MSCZ-COUNT
    SUBDIR-COUNT
    SUBDIRS
    SAMPLE-FILES
    FLAGS
));

for my $semester (sort immediate_dir_names($SOURCE_ROOT)) {
    next if ignore_dir($semester);

    my $semester_path = "$SOURCE_ROOT/$semester";

    for my $entry (sort immediate_dir_names($semester_path)) {
        next if ignore_dir($entry);

        my $entry_path = "$semester_path/$entry";

        if (is_container($entry)) {
            my $group = group_name($entry);

            for my $piece (sort immediate_dir_names($entry_path)) {
                next if ignore_dir($piece);

                my $piece_path = "$entry_path/$piece";
                process_piece($semester, $group, $piece, $piece_path);
            }
        }
        else {
            process_piece($semester, "", $entry, $entry_path);
        }
    }
}

close $out;
print "Wrote $OUT\n";

sub process_piece {
    my ($semester, $group, $piece, $piece_path) = @_;

    my $info = inspect_piece_dir($piece_path);

    return unless $info->{pdf_count} || $info->{mscz_count};

    print $out csv_row(
        $semester,
        $group,
        $piece,
        relpath($piece_path),
        $info->{pdf_count},
        $info->{mscz_count},
        scalar @{ $info->{subdirs} },
        join(" | ", @{ $info->{subdirs} }),
        join(" | ", @{ $info->{samples} }),
        join(" | ", @{ $info->{flags} }),
    );
}

sub inspect_piece_dir {
    my ($root) = @_;

    my %info = (
        pdf_count  => 0,
        mscz_count => 0,
        subdirs    => [],
        samples    => [],
        flags      => [],
    );

    my %subdir_seen;
    my %flag_seen;

    my @stack = ($root);

    while (@stack) {
        my $dir = shift @stack;

        opendir(my $dh, $dir) or next;

        while (my $name = readdir($dh)) {
            next if $name =~ /^\./;

            my $path = "$dir/$name";

            if (-d $path) {
                $subdir_seen{$name} = 1;

                if ($name =~ /^old/i || $name =~ /ignore/i || $name =~ /do[-_ ]?not[-_ ]?use/i) {
                    $flag_seen{"HAS-SKIP-DIR:$name"} = 1;
                    next;
                }

                $flag_seen{"HAS-SOURCE-DIR:$name"} = 1
                    if $name =~ /source/i;

                $flag_seen{"HAS-VN-2B-DIR:$name"} = 1
                    if $name =~ /violin.*2.*b/i || $name =~ /2.*b.*part/i;

                push @stack, $path;
            }
            elsif (-f $path) {
                if ($name =~ /\.pdf$/i) {
                    $info{pdf_count}++;
                    push @{ $info{samples} }, $name if @{ $info{samples} } < 8;
                }
                elsif ($name =~ /\.mscz$/i) {
                    $info{mscz_count}++;
                    push @{ $info{samples} }, $name if @{ $info{samples} } < 8;
                }
            }
        }

        closedir($dh);
    }

    $info{subdirs} = [sort keys %subdir_seen];
    $info{flags}   = [sort keys %flag_seen];

    return \%info;
}

sub immediate_dir_names {
    my ($dir) = @_;

    opendir(my $dh, $dir) or return;

    my @names;
    while (my $name = readdir($dh)) {
        next if $name =~ /^\./;
        push @names, $name if -d "$dir/$name";
    }

    closedir($dh);
    return @names;
}

sub ignore_dir {
    my ($name) = @_;
    return grep { $name =~ $_ } @IGNORE_DIRS;
}

sub is_container {
    my ($name) = @_;
    return grep { $name =~ $_ } @CONTAINER_DIRS;
}

sub group_name {
    my ($name) = @_;
    return "ALPHA" if $name =~ /^ALPHA_/i;
    return "OMEGA" if $name =~ /^OMEGA_/i;
    return "PRE-ORCHESTRA" if $name =~ /^PRE-ORCHESTRA/i;
    return "";
}

sub relpath {
    my ($path) = @_;
    $path =~ s{^\Q$SOURCE_ROOT\E/?}{};
    return $path;
}

sub csv_row {
    return join(",", map { csv($_) } @_) . "\n";
}

sub csv {
    my ($s) = @_;
    $s = "" unless defined $s;
    $s =~ s/"/""/g;
    return qq{"$s"};
}
