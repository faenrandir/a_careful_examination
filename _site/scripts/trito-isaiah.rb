#!/usr/bin/env ruby

# analyzes the probability that a _block_ of chapters would be pulled from
# trito-Isaiah

# notice that most of Isaiah in the BoM was pulled from two blocks of
# consecutive chapters (see http://www.mormonhandbook.com/home/isaiah-in-the-book-of-mormon.html)

# first block
# Isaiah 2	2 Nephi 12
# Isaiah 3	2 Nephi 13
# Isaiah 4	2 Nephi 14
# Isaiah 5	2 Nephi 15
# Isaiah 6	2 Nephi 1
# Isaiah 7	2 Nephi 17
# Isaiah 8	2 Nephi 18
# Isaiah 9	2 Nephi 19
# Isaiah 10	2 Nephi 20
# Isaiah 11	2 Nephi 21
# Isaiah 12	2 Nephi 22
# Isaiah 13	2 Nephi 23
# Isaiah 14	2 Nephi 24

# second block
# Isaiah 48	1 Nephi 20
# Isaiah 49	1 Nephi 21
# Isaiah 50	2 Nephi 7
# Isaiah 51	2 Nephi 8
# Isaiah 52	3 Nephi 20
# Isaiah 53	Mosiah 14
# Isaiah 54	3 Nephi 22

if ARGV && ['--verbose', '-v'].include?(ARGV[0])
  $VERBOSE = true
end

def putsv(*args)
  if $VERBOSE
    puts(*args)
  end
end

def display_label(label, outline_length=78)
  puts "-" * outline_length
  puts label
  puts "-" * outline_length
end

def display_results(label, results)
  in_trito, not_in_trito = results.values_at(:in_trito, :not_in_trito)
  total_possible = in_trito + not_in_trito
  prob_in_trito = (in_trito.to_f / total_possible).round(3)
  prob_not_in_trito = (not_in_trito.to_f / total_possible).round(3)

  display_label(label)
  puts <<~HEREDOC
    probability in trito: #{prob_in_trito} (#{in_trito} / #{total_possible})
    probability not in trito: #{prob_not_in_trito} (#{not_in_trito} / #{total_possible})
  HEREDOC
  puts
end

def display_simple_results(label, prob_in, prob_out)
  display_label(label)
  puts <<~HEREDOC
    probability in trito: #{prob_in}
    probability not in trito: #{prob_out}
  HEREDOC
  puts
end

ALL_ISAIAH_CHAPTERS = (1..66)
TRITO_ISAIAH = (55..66)

class Chunk
  attr_accessor :range

  def initialize(start, length)
    @range = start..(start + length - 1)
  end

  def start
    @range.begin
  end

  def finish
    @range.end
  end

  def ranges_overlap?(range_a, range_b)
    range_b.begin <= range_a.end && range_a.begin <= range_b.end 
  end

  def overlap?(chunk)
    self.ranges_overlap?(self.range, chunk.range)
  end

  def valid?
    [start, finish].all? do |num|
      ALL_ISAIAH_CHAPTERS.include?(num)
    end
  end

  def in_trito_isaiah?
    [start, finish].any? {|num| TRITO_ISAIAH.include?(num) }
  end

  def to_s
    "#{start}:#{finish}"
  end
end

CHUNK1_LENGTH = 13
CHUNK2_LENGTH = 7

in_trito = 0
not_in_trito = 0
overlapping = 0
ALL_ISAIAH_CHAPTERS.each do |chunk1_start|
  chunk1 = Chunk.new(chunk1_start, CHUNK1_LENGTH)
  ALL_ISAIAH_CHAPTERS.each do |chunk2_start|
    chunk2 = Chunk.new(chunk2_start, CHUNK2_LENGTH)
    if [chunk1, chunk2].all?(&:valid?)
      if chunk1.overlap?(chunk2)
        overlapping += 1
        putsv "OVERLAPPING: #{chunk1} #{chunk2}"
      elsif [chunk1, chunk2].any?(&:in_trito_isaiah?)
        in_trito += 1
        putsv "IN TRITO: #{chunk1} #{chunk2}"
      else
        not_in_trito += 1
        putsv "NOT IN TRITO: #{chunk1} #{chunk2}"
      end
    end
  end
end

total_possibilities = in_trito + not_in_trito

results = {
  in_trito: in_trito,
  not_in_trito: not_in_trito,
}
putsv "overlapping: #{overlapping}"
display_results("two chunks, one 13 chapters and the other 7", results)

# ---

# probability of second chunk being trito Isaiah assume the first chunk can be
# accounted for as merely starting towards the very beginning of Isaiah.

REMAINING_ISAIAH_CHAPTERS = (15..66)

in_trito = 0
not_in_trito = 0

chunk1 = Chunk.new(2, CHUNK1_LENGTH)
REMAINING_ISAIAH_CHAPTERS.each do |chunk2_start|
  chunk2 = Chunk.new(chunk2_start, CHUNK2_LENGTH)
  if chunk2.valid?
    if chunk2.in_trito_isaiah?
      in_trito += 1
      putsv "IN TRITO: #{chunk1} #{chunk2}"
    else
      not_in_trito += 1
      putsv "NOT IN TRITO: #{chunk1} #{chunk2}"
    end
  end
end

results = {
  in_trito: in_trito,
  not_in_trito: not_in_trito,
}
display_results("7 chapter chunk assuming first chunk at beginning", results)


# http://stattrek.com/online-calculator/hypergeometric.aspx
# 66 chapters of Isaiah
# 54 of them are NOT trito-Isaiah
# 20 chapters inserted into the BoM
# what is the probability that 20 chapters will not be in trito-Isaiah?
display_simple_results("hyperg. dist; pop:66, successes:54, sample:20, >= 20 required", 0.992095964, 0.007904036)

# http://stattrek.com/online-calculator/hypergeometric.aspx
# If we assume that chapters 1-14 are accounted for by the BoM manuscript creator
# merely taking from the beginning of the book, then what is the probability
# that a trito-Isaiah chapter would be included in the next 7 chapters, chosen
# at random (without replacement)?
# 51 remaining chapters of Isaiah (after removing first 14)
# 40 of the remaining chapters are NOT trito-Isaiah
# 7 chapters to be inserted into the BoM
# what is the probability that 7 chapters will not be in trito-Isaiah?
display_simple_results("hyperg. dist (only 7 chapters); pop:51, successes:40, sample:7, >= 7 required", 0.838967446, 0.161032554)
