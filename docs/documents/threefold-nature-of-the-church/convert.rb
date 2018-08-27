#!/usr/bin/env ruby

class String
  def string_between_markers(marker1, marker2)
    self[/#{Regexp.escape(marker1)}(.*?)#{Regexp.escape(marker2)}/m, 1]
  end
end


filename = ARGV.shift

base = %w(pandoc --smart --toc --number-sections --standalone) + [filename]

pdf_outfile = "threefold-nature-of-the-church.pdf"
html_outfile = "threefold-nature-of-the-church.html"

html_options = %w(--toc-depth 1 --to html5)
pdf_options = %w(--toc-depth 2 --variable urlcolor=Blue)

[base + html_options + ['-o', html_outfile], base + pdf_options + ['-o', pdf_outfile]].each do |args|
  `#{args.join(' ')}`
end

document = IO.read(html_outfile)

IO.write("for_mormonbandwagon.html", document.string_between_markers('</header>', '</body>'))
