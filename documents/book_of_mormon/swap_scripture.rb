#!/usr/bin/env ruby


def swap_scripture(line)
  line = line.chomp
  begin_quote = ' “'
  begin_cell_str = '<td valign="top">'

  if line.include?("<td valign")
    parts = line.split(begin_cell_str)
    last_parts = parts.pop.split(begin_quote)
    last_parts[-1].sub!("</tr>",'')
    last_parts.reverse!
    last_parts[0] = '“' + last_parts[0]
    last_parts[-1] += '</td></tr>'
    parts.push(*last_parts).join(begin_cell_str) + "\n"
  else
    line
  end
end


lines = IO.readlines(ARGV.shift)

lines.each {|line| puts swap_scripture(line) }

