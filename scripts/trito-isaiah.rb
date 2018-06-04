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

CHUNK1_LENGTH = 14
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
        puts "OVERLAPPING: #{chunk1} #{chunk2}"
      elsif [chunk1, chunk2].any?(&:in_trito_isaiah?)
        in_trito += 1
        puts "IN TRITO: #{chunk1} #{chunk2}"
      else
        not_in_trito += 1
        puts "NOT IN TRITO: #{chunk1} #{chunk2}"
      end
    end
  end
end

total_possibilities = in_trito + not_in_trito

puts "overlapping: #{overlapping}"
puts "IN TRITO: #{in_trito}"
puts "NOT IN TRITO: #{not_in_trito}"
puts "total possibilities: #{total_possibilities}"
puts "probability in trito: #{in_trito.to_f / total_possibilities}"
puts "probability not in trito: #{not_in_trito.to_f / total_possibilities}"

__END__
(overlapping): 1018

IN TRITO: 972
NOT IN TRITO: 1190
total possibilities: 2162

probability of a chapter in trito: 0.4495837187789084
probability of a chapter not in trito: 0.5504162812210915
