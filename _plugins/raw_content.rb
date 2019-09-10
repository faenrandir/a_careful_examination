
module Jekyll

  class RawContent < Generator

    def generate(site)
      site.posts.docs.each do |doc|
        doc.data['raw_content'] = doc.content
      end
    end
  end

end
