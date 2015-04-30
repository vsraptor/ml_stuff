#!/usr/bin/env perl
use strict;
use Getopt::Long qw(:config no_ignore_case);;
use Data::Dumper;

our %opts = ();
our %stats = ();
our $VERSION = '0.1';
our $file_name = '';

sub parse_args {
	GetOptions(
		\%opts, 'l|lines', 'm|chars', 'c|bytes', 'L|max-line-lenght', 'w|words', 'h|help', 'v|version', 'files0-from=s',
		'<>' => sub { push @{ $opts{file_names} }, @_ }
	)
}

sub say { print @_; print "\n" }

sub version { say "wc.pl : version $VERSION" }

sub help {
print <<HELP;
NAME
       wc.pl - print newline, word, and byte counts for each file

SYNOPSIS
       wc.pl [OPTION]... [FILE]...
       wc.pl [OPTION]... --files0-from=F

DESCRIPTION
       Print  newline,  word,  and byte counts for each FILE, and a total line if more than one FILE is specified.  With no FILE, or when FILE is -, read
       standard input.  A word is a non-zero-length sequence of characters delimited by white space.  The options below  may  be  used  to  select  which
       counts are printed, always in the following order: newline, word, character, byte, maximum line length.

       -c, --bytes
              print the byte counts

       -m, --chars
              print the character counts

       -l, --lines
              print the newline counts

       --files0-from=F
              read input from the files specified by NUL-terminated names in file F; If F is - then read names from standard input

       -L, --max-line-length
              print the length of the longest line

       -w, --words
              print the word counts

       --help display this help and exit

       --version
              output version information and exit

HELP
}

sub extract_filenames {
	my $fname = shift;
	my @fnames = ();
	open my $fh, "<$fname" or die "Cant open $fname :$!";
	my $str = '';
	{ local $/ = '\0'; $str = <$fh> }
	close $fh;
	push @fnames, split /\0/, $str;
	return @fnames
}

sub process_file {
	my $fname = shift;

	my $fh;
	if ($fname eq 'stdin') { $fh = *STDIN }
	else { open $fh, "<$fname" or die "Cant open $fname :$!" }

	while (<$fh>) {
		$stats{$fname}{chars} += length $_;
		$stats{$fname}{lines} ++;
		#wc does not count new line !!! but does for chars and bytes
		$stats{$fname}{mll} = length($_) - 1 if length($_)-1 > $stats{$fname}{mll};

		#for word counting we need to trim white-spaces
		(my $str = $_) =~ s/^\s+//;
		$str =~ s/\s+$//;
		$stats{$fname}{words} += split /\s+/, $str;


		{
			use bytes;
			$stats{$fname}{bytes} += length $_;
		}
	}
	close $fh unless $fname eq 'stdin';

	$stats{total}{chars} += $stats{$fname}{chars};
	$stats{total}{lines} += $stats{$fname}{lines};
	$stats{total}{words} += $stats{$fname}{words};
	$stats{total}{bytes} += $stats{$fname}{bytes};
	$stats{total}{mll} = $stats{$fname}{mll} if $stats{total}{mll} < $stats{$fname}{mll}; 

}


sub file_stats {
	my $fname = shift;
	my %show = ();

	my $none = $opts{l} || $opts{m} || $opts{c} || $opts{L} || $opts{w};
	if ($opts{l} || not $none) {
		$show{lines} = $stats{$fname}{lines};
	}
	if ($opts{m} || not $none) {
		$show{chars} = $stats{$fname}{chars};
	}
	if ($opts{c}) {
		$show{bytes} = $stats{$fname}{bytes};
	}
	if ($opts{L}) {
		$show{mll} = $stats{$fname}{mll};
	}
	if ($opts{w} || not $none) {
		$show{words} = $stats{$fname}{words};
	}

	my $str = join ' ', map {$show{$_}} grep {$show{$_}} qw(lines words chars bytes mll);
	say "$str $fname";

}

sub process_files {
	my @fnames = @_;
	foreach my $f (@fnames) {
		process_file $f;
		file_stats $f;
	}
}

sub process {

	help, return if $opts{h};
	version, return if $opts{v};

	my @fnames = ();
	if ($opts{'files0-from'}) {
		@fnames = extract_filenames $opts{'files0-from'}
	} else {
		push @fnames, @{$opts{file_names}} if $opts{file_names}
	}

	if (-p STDIN) {
		process_file 'stdin';
		file_stats 'stdin';
	}
	if (@fnames) {
		process_files @fnames;
		file_stats 'total' if scalar @fnames > 1;
	}
}


parse_args();
process();
