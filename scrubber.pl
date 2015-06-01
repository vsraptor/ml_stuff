#!/usr/bin/env perl
use strict;
use Mojo::UserAgent;
use Mojo::DOM;

#specify the HTML element that contain the content you are interested
use constant CONTENT_ELEMENT => 'div.body-content';
#where to generate the html files
use constant DEST_DIR => './tmp';
#object used to fetch the pages
our $ua = new Mojo::UserAgent;

#List of urls you want to fetch
our @urls = (
'-Theory-of-Value-',
'mises.org/library/what-does-marginality-mean',
'mises.org/library/economics-slushy-drinks',
'mises.org/library/problems-cost-theory-value',
'mises.org/library/subjective-value-theory',
'mises.org/library/subjective-value-and-market-prices',
'-Capital-and-Interest-',
'mises.org/library/importance-capital-theory',
'mises.org/library/why-do-capitalists-earn-interest-income',
'mises.org/library/abstinence-theory-interest',
'mises.org/library/thinking-clearly-about-capital-interest-and-income',
'-Banking-and-money-',
'mises.org/library/fractional-reserve-banking-question',
'mises.org/library/our-money-based-debt',
'mises.org/library/rothbard-land-prices',
'mises.org/library/origin-money-and-its-value',
'mises.org/library/money-vs-wealth',
'mises.org/library/have-anthropologists-overturned-menger',
'mises.org/library/why-money-doesn%E2%80%99t-measure-value',
'mises.org/library/lost-maze-money-aggregates',
'-Debunking-',
'mises.org/library/gnome-thought-experiment',
'mises.org/library/critical-flaw-keyness-system',
'mises.org/library/upside-down-world-mmt',
);

#used to generate the filename which we use to save on the hard-drive
sub get_filename {
	my %a = @_;
	#glean the file name from the url
	(my $fname) = $a{url} =~ m!.+/(.+)!;
	return $fname
}

sub get_head_str {
	my %a = @_;
	#we want page header to be clean of dashes
	(my $head_str = $a{str}) =~ s/-/ /g;
	return $head_str
}

sub full_path {
	my %a = @_;
	#generate number to prepend to the filename, so we can preserve the order for pdf generation
	my $fn = sprintf "%02d", $a{idx};
	return  DEST_DIR . "/$fn$a{fname}.html"
}

sub save_html {
	my %a = @_;
	open my $fh, ">$a{full_name}" or die $!;
	print $fh $a{header};
	print $fh ${$a{str}};
	close $fh;
}

sub fetch_and_extract {
	my %a = @_;
	my ($tx,$dom) = (0,0);
	#fetch the html page
	$tx = $ua->max_redirects(3)->get($a{url})->res->body;
	#make it DOM object so we can traverse the HTML
	$dom = new Mojo::DOM($tx);
	#extract the content of html element
	my $str = $dom->find(CONTENT_ELEMENT);
	$str =~ s/[^[:ascii:]]+//g;#clean up non ascii characters
	return \$str
}

sub format_header {
	my %a = @_;
	return "<h1 style='color:#556698'>" . $a{str} . "</h1><hr>\n"	if $a{type} eq 'normal';
	return "<br><br><br><br><hr><h1 style='font-size:35pt;color:#556698'>" . $a{str} . "</h1><hr>\n";
}

#LOOP over all URL's
for my $i (0 .. $#urls) {

	print "$urls[$i]\n";
	#initialize vars
	my ($str_ref,$fname,$header) = (0,0,0);

	if ($urls[$i] =~ /^-/) {#Section page if it starts with dash

		$fname = $urls[$i];
		$str_ref = \"";#"
		#format the Section page header
		$header = format_header type => 'section', str => $fname

	} else {# Normal page

		$str_ref = fetch_and_extract url => $urls[$i];

		$fname = get_filename url => $urls[$i];
		#header is build from the filename
		my $head_str = ucfirst get_head_str str => $fname;
		$header = format_header type => 'normal', str => $head_str

	}

	my $full_name = full_path idx => $i, fname => $fname;
	save_html full_name => $full_name, str => $str_ref, header => $header;
}

#To convert html files to PDF, run this script inside the dir where you generated the HTML files
# wkhtmltopdf *html rm.pdf
