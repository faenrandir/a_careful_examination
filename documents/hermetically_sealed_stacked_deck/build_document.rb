#!/usr/bin/ruby


OUTFILE = "hermetically-sealed-systems-in-lds-thought.pdf"
File.unlink(OUTFILE) if File.exists?(OUTFILE)

inkscape_files = Dir['*.svgz'].reject {|v| v =~ /standalone/}.sort

base_cmd = ["svg_to_pxx.rb"]

inkscape_files.each do |file|
  cmd = base_cmd + [file]
  final_cmd = cmd.join(" ")
  system final_cmd
end

Dir['*.odt'].each do |odt_file|
  system "odf_to_pdf.rb #{odt_file}"
end

pdfs = Dir["*.pdf"].reject {|v| v=~ /standalone/}.sort

`pdftk #{pdfs.join(" ")} cat output #{OUTFILE}`

pdfs.each {|file| File.unlink(file) }
