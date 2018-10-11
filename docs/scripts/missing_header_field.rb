#!/usr/bin/env ruby

require 'yaml'

if ARGV.size < 2
  puts "usage: #{File.basename(__FILE__)} <field> **/*.md"
  exit
end

def has_proper_header(lines)
  beginning_lines = lines[0..20]
  beginning_lines.select {|line| line.chomp == '---' }.size >= 2
end

def read_header(file, lines)
  init = lines.shift
  if init.chomp != "---"
    abort "#{file} has very improper header"
  end
  header = lines.take_while {|line| line.chomp != '---'}.join
  YAML.load(header)
end

field = ARGV.shift

files = ARGV

missing_field = []
improper_headers = []
files.each do |file|
  next if file.start_with?('docs')
  lines = IO.readlines(file)
  if has_proper_header(lines)
    header = read_header(file, lines)
    unless header.keys.include?(field)
      missing_field << file
    end
  else
    improper_headers << file
  end
end

puts "-" * 80
puts "Missing field `#{field}`"
puts "-" * 80
missing_field.each do |file|
  puts file
end

puts "-" * 80
puts "Improper headers!"
puts "-" * 80
improper_headers.each do |file|
  puts file
end
