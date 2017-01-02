#!/usr/bin/ruby

non_links = ["pray_about_bom"]

DIAGRAM_BOOKMARKS = [
  "Do not seek revelation on that which contradicts the Brethren",
  "Revelations contradicting the Brethren are not from God",
  "All answers to prayer are correct",
  "Follow Moroni's Promise to know that the Book of Mormon is true",
  "Only the ignorant and proud disagree with accepted LDS doctrine",
]

insertion_lines = DIAGRAM_BOOKMARKS.flat_map.with_index do |bookmark, index|
  ["BookmarkBegin", "BookmarkTitle: #{index+1}-#{bookmark}", "BookmarkLevel: 1", "BookmarkPageNumber: #{index+3}"]
end

INSERT_AFTER = "BookmarkPageNumber: 2"


FILE_OUTPUT_BASE = "hermetically-sealed-systems-in-lds-thought"
DATA_FILE = "data.txt"
INSERTED_DATA_FILE = "data-inserted.txt"
TMP_FILE = FILE_OUTPUT_BASE + "-tmp.pdf"
FINAL_OUTPUT = FILE_OUTPUT_BASE + ".pdf"

[FINAL_OUTPUT, DATA_FILE, TMP_FILE].each do |file|
  File.unlink(file) if File.exist?(file)
end

inkscape_files = Dir['*.svgz'].sort

base_cmd = ["svg_to_pxx.rb", "-t"]

inkscape_files.each do |file|
  cmd = base_cmd + [file]
  cmd << "--link" unless non_links.any? {|non_link| file.include?(non_link) }
  final_cmd = cmd.join(" ")
  system final_cmd
end

article = Dir['*.odt'].first

system "odf_to_pdf.rb #{article}"

pdfs = Dir["*.pdf"].sort

`pdftk #{pdfs.join(" ")} cat output #{TMP_FILE}`
`pdftk #{TMP_FILE} dump_data_utf8 output #{DATA_FILE}`

lines = IO.readlines(DATA_FILE).map(&:chomp)
insert_after = lines.index {|line| line == INSERT_AFTER } + 1
lines.insert(insert_after, *insertion_lines)

File.write(INSERTED_DATA_FILE, lines.join("\n"))

`pdftk #{TMP_FILE} update_info_utf8 #{INSERTED_DATA_FILE} output #{FINAL_OUTPUT}`

(pdfs + [TMP_FILE, DATA_FILE, INSERTED_DATA_FILE]).each do |file|
  File.unlink(file)
end
