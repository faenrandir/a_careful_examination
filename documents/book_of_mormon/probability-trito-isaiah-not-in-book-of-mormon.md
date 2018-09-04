---
title: "How likely was trito-Isaiah to have been avoided at random in the Book of Mormon translation?"
permalink: /how-likely-trito-isaiah-avoided-in-bom/
doctype: snippet
layout: page
---

### Introduction

It [has been claimed](https://www.reddit.com/r/mormon/comments/8nts0v/a_response_to_the_recently_posted_document_on_the/e02105x/) that the absence of Trito-Isaiah in the Book of Mormon supports a claim for the historicity of the Book of Mormon:

> We can probably agree that there is no way JS could have known about deutero and trito Isaiah. If he knew about it, he certainly would be careful with quoting anything beyond first Isaiah, but we know he did. The thing is, critics only talk about deutero-Isaiah, but the absence of trito-Isaiah strongly supports JS as prophet. If JS didn't know about these Isaiah issues he had nothing to guide his choices of which chapters to include. 21 Isaiah chapters are quoted in the BoM. If you randomly choose 21 Isaiah chapters, there is a less than 1% probability that you will not choose any of the chapters 56-66 (trito-Isaiah)!

> Let's compare that with deutero-Isaiah. Would you say it's less than 1% probability that a version of deutero-Isaiah was written initially sometime between Isaiah and Lehi? I certainly wouldn't. We know little about the origins of specific bible texts, but scholars know a bit about the general process. It's not someone sitting down and writing a text, never to be altered. There are initial oral versions, preliminary written versions, redaction, translations back and forth, etc. For instance, there could have been a text at Lehi's time, slightly altered in the exile period (like including "Cyrus"). We know very little about this, so I would not place a bet on this with the less than 1% odds. My conclusion is that the deutero/trito-Isaiah issue combined supports my belief.

I agree that on some level the absence of trito-Isaiah in the Book of Mormon is evidence in favor of an ancient origin.  However, a closer examination of the likelihood that trito-Isaiah could randomly be excluded from the Book of Mormon lessens the significance of the find.

### Choosing the right model

If we assume that Smith were drawing upon Isaiah chapters randomly, then the above is absolutely correct in probability assessment.  The probability that 20 Isaiah chapters could have been selected at random from the set of 66 Isaiah chapters without once selecting a chapter from trito-Isaiah (chapters 55-66, or 12 chapters) is properly modeled by a cumulative hypergeometric distribution, and yields a probability of 0.0079, or roughly 0.8% that someone could make such a biased selection randomly.

    # http://stattrek.com/online-calculator/hypergeometric.aspx
    # hyperg. dist; pop:66, successes:54, sample:20, >= 20 required
    probability in trito: 0.992095964
    probability not in trito: 0.007904036

However, 13 of the first 14 chapters of Isaiah are used, so we can hardly refer to chapter selection as truly random.  If we merely posit that Smith selected a 13 chapter chunk from the beginning, what is the probability that the remaining 7 chapters would not have been pulled from Trito-Isaiah?  Using the same distribution as above but with modified parameters, we get a probability of 0.16 or 16% that a person would _not_ randomly select a trito-Isaiah chapter after selecting a block of 13 chapters from the beginning of the book.

    # http://stattrek.com/online-calculator/hypergeometric.aspx
    # hyperg. dist (only 7 chapters); pop:51, successes:40, sample:7, >= 7 required
    probability in trito: 0.838967446
    probability not in trito: 0.161032554

But we may even be too generous here.  The vast majority of all other Isaiah citations come from just seven other consecutive chapters, Isaiah 48--54.  Again, the distribution here can't be called "random" in the least---these are _blocks_ of chapters which seem to have been selected.  What happens if we go back and ask how likely it is that two blocks of chapters, one 13 chapters long and one 7 chapters long, can be randomly selected from Isaiah without selecting a single trito-Isaiah chapter?  I wrote up [a script](https://github.com/faenrandir/a_careful_examination/blob/e5a43715b09837fcabdc6664f3f0d00b0fbacaf1/scripts/trito-isaiah.rb) to enumerate every possibility (also throwing out overlaps and such) and calculated the probabilities.  Turns out the probabibility that _both_ chunks could randomly be selected from non trito chapters is 0.56, or 56%.  So, thinking about the selection as two random chunks now pushes the probability _in favor of Smith getting lucky_---he was more likely to grab continuous chunks that never touch trito-Isaiah than do touch it.

    # trito-isaiah.rb --verbose  # will enumerate every possibility
    # two chunks, one 13 chapters and the other 7
    probability in trito: 0.441 (996 / 2256)
    probability not in trito: 0.559 (1260 / 2256)

Finally, if we assume that the first 13 chapters can be explained by selecting, essentially, the first chapters from the book of Isaiah, and we ask what is the probability that another chunk of 7 chapters would include a single trito-Isaiah chapter, the odds are that Joseph _would not_ have selected an additional seven chapter chunk with a single chapter of trito-Isaiah in it (74% probability that he would not have selected a seven chapter chunk that included a single trito-Isaiah chapter).  Again, I calculated the probability by enumerating every possibility (since I already had [the basic script](https://github.com/faenrandir/a_careful_examination/blob/e5a43715b09837fcabdc6664f3f0d00b0fbacaf1/scripts/trito-isaiah.rb)).

    # trito-isaiah.rb --verbose  # will enumerate every possibility
    # 7 chapter chunk assuming first chunk at beginning
    probability in trito: 0.261 (12 / 46)
    probability not in trito: 0.739 (34 / 46)

In conclusion, it is difficult to argue that the chapters quoted in the Book of Mormon were randomly selected, and selecting blocks of consecutive chapters shifts the probability in favor of Smith randomly avoiding a single trito-Isaiah chapter.

### The Remaining Isaiah Problem

The above analysis is important for demonstrating that Smith could have randomly avoided the trito-Isaiah chapters with only a minor amount of luck.  Still, it misses the deeper point about the Isaiah found in the Book of Mormon: We don't expect to see deutero-Isaiah in the form we see it in, and, according to Grant Hardy, we don't even expect to see Isaiah 2--14 in the form we find it.  Consider [his words](https://github.com/faenrandir/a_careful_examination/blob/e5a43715b09837fcabdc6664f3f0d00b0fbacaf1/documents/book_of_mormon/the_puzzle_of_the_King_James_Version__Grant_Hardy.md):

> For non-Mormon scholars, imagining the Brass Plates (ostensibly Nephi’s source) as a historic artifact from 600 BC is made even more difficult by the presence in the Book of Mormon of chapters from Second Isaiah (Isa. 40--55), which scholarly consensus for more than a century has attributed to the time of the Exile or even later (though, interestingly enough, the Book of Mormon never cites Third Isaiah [chs. 56--66]). **Latter-day Saints sometimes brush such criticism aside, asserting that such interpretations are simply the work of academics who do not believe in prophecy, but this is clearly an inadequate (and inaccurate) response to a significant body of detailed historical and literary analysis**.[28] William Hamblin has suggested that the problem might be alleviated if we regard Second Isaiah as a prophet contemporary with Nephi, but even this is not an entirely satisfactory solution.[29] Recent Isaiah scholarship has moved away from the strict differentiation of the work of First and Second Isaiah (though still holding to the idea of multiple authorship) in favor of seeing the book of Isaiah as the product of several centuries of intensive redaction and accretion. In other words, **even Isaiah 2--14 would have looked very different in Nephi’s time than it did four hundred years later at the time of the Dead Sea Scrolls, when it was quite similar to what we have today**. (emphasis added)
