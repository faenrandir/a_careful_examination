#!/usr/bin/env ruby

# https://www.reddit.com/r/exmormon/comments/5vs93e/table_of_the_dates_of_joseph_smiths_marriages/

require 'date'
require 'yaml'

data=<<END
1827-01-18 |EMMA HALE|[January 18, 1827]
1836-07 |FANNY ALGER|Marriage Date Unknown (Probably Late 1835 or Early 1836)
1841-04-05 |LOUISA BEAMAN|Sealed April 5, 1841
1841-10-27 |ZINA DIANTHA HUNTINGTON|Sealed October 27, 1841
1841-12-11 |PRESENDIA LATHROP HUNTINGTON|Sealed December 11, 1841
1842-01-06 |AGNES MOULTON COOLBRITH|Sealed January 6, 1842
1842-02 |MARY ELIZABETH ROLLINS|Sealed February 1842
1842-03-09 |PATTY BARTLETT|Sealed March 9, 1842
1842-04 |MARINDA NANCY JOHNSON|Two Sealing Dates April 1842 and May 1843
1842-06-01 |ELVIRA ANNIE COWLES|Sealed June 1, 1843
1842-06-29 |ELIZA R. SNOW|Sealed June 29, 1842
1842-07 |DELCENA DIDAMIA JOHNSON|Sealed prior to July 1842
1842-07-27 |SARAH ANN WHITNEY|Sealed July 27, 1842
1842-10 |MARTHA McBRIDE|Sealed Summer 1842
1843-02 |RUTH VOSE|Sealed February 1843
1843-03-04 |ELIZA PARTRIDGE|Sealed March 4 and May 11, 1843
1843-03-04 |EMILY DOW PARTRIDGE|Sealed March 4 and May 11, 1843
1843-04 |ALMERA WOODARD JOHNSON|Sealed April 1843
1843-05 |HELEN MAR KIMBALL|Sealed May 1843
1843-05 |MARIA LAWRENCE|Sealed May 1843
1843-05 |SARAH LAWRENCE|Sealed May 1843
1843-05-01 |LUCY WALKER|Sealed May 1, 1843
1843-05-18 |SYLVIA SESSIONS|Sealed Between Nov. 19, 1842 and May 18, 1843
1843-06-12 |RHODA RICHARDS|Sealed June 12, 1843
1843-07 |DESDEMONA FULLMER|Sealed July 1843
1843-07 |FLORA ANN WOODWORTH|Sealed Spring 1843
1843-09-20 |MALISSA LOTT|Sealed September 20, 1843
1843-10 |HANNAH ELLS|Sealed Prior to the Summer of 1843
1843-10 |OLIVE G. FROST|Sealed Summer of 1843
1843-11-02 |FANNY YOUNG|Sealed November 2, 1843
END

Wife = Struct.new(:date, :name, :verbiage) do
  def to_s
    %Q(#{name} "#{verbiage}")
  end
end

COMMON_YEAR_DAYS_IN_MONTH = [nil, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

def days_in_month(month, year)
  days = COMMON_YEAR_DAYS_IN_MONTH[month]
  days += 1 if month == 2 && ::Date.gregorian_leap?(year)
  days
end

WIVES = data.split("\n").map do |line|
  date_str, caps_name, verbiage = line.chomp.split(/\s*\|\s*/)

  year_str, month_str, day_str = date_str.split("-")
  valid_date_str =
    if !day_str
      # set to last day of the month
      num_days_in_month = days_in_month(month_str.to_i, year_str.to_i)
      [year_str, month_str, num_days_in_month].join("-")
    else
      date_str
    end

  Wife.new(
    Date.parse(valid_date_str),
    caps_name.split.map(&:downcase).map(&:capitalize).join(" "),
    verbiage
  )
end


if __FILE__ == $0
  if ARGV.size == 0
    puts "usage: #{File.basename(__FILE__)} YYYY-MM-DD"
    puts "output: The most conservative estimate of the number of wives Joseph"
    puts "Smith, Jr. had at the end of that day."
    exit
  end

  date_str = ARGV.shift
  comparison_date = Date.parse(date_str)
  wives_on_or_before = WIVES.take_while {|wife| wife.date <= comparison_date}
  output = {
    'count' => wives_on_or_before.size,
    'wives' => wives_on_or_before.map(&:to_s)
  }
  puts "The most conservative estimate of the number of wives Joseph Smith had"
  puts "either been married to or sealed to by #{comparison_date} based on established"
  puts "dates given in josephsmithspolygamy.org is: **#{wives_on_or_before.size}**"
  puts ""
  puts output['wives'].to_yaml.split("\n")[1..-1].join("\n")

  #puts output.to_yaml
end
