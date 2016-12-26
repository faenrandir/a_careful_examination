#!/usr/bin/env ruby

require 'shellwords'
# --smart gets me proper curly quotes and apostrophes!
# but they will not look right unless --standalone and/or --to html5 are also used
default_options = "--smart --to html5"
#default_options = "--smart --standalone --to html5"
#default_options = "--smart --standalone --to html5 --number-sections"

if ARGV.size == 0
  puts "usage: #{File.basename(__FILE__)} [OPT] <file>.md ..."
  puts "outputs <file>.html ..."
  puts
  puts "options on by default: "
  puts "   #{default_options}"
  exit
end

ARGV.each do |file|
  base = file.chomp(File.extname(file))
  outfile = base + '.html'
  html = `pandoc #{default_options} #{Shellwords.escape(file)}`
  File.write(outfile, html)
end
