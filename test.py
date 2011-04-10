#!/usr/bin/env python

import thebestspinner

tbs = thebestspinner.Api("seo@searchenginedominator.co.uk", "0d236e820f47f469a20bcfe363eec209", 50)

print tbs.apiQuota()

#original_text = "This is the text we want to spin"

#spin_text = tbs.identifySynonyms(original_text)
#print spin_text

#ev_text = tbs.replaceEveryonesFavorites(spin_text)
#print ev_text

print tbs.replaceEveryonesFavorites("Losing weight can be a difficult thing to do.", 3, 1);

print tbs.apiQuota()
