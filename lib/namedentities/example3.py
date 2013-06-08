from namedentities import named_entities

u = 'both em\u2014and&#x2013;dashes&hellip;'
print(named_entities(u))