"""Named HTML entities are much easier to comprehend than numeric entities. This
module helps convert between the more typical numerical entiies and the more
attractive named entities. """

# Primarily a packaging of Ian Beck's work from
# http://beckism.com/2009/03/named_entities_python/

# There are too many little differences in Python 2 and Python 3 string
# handling syntax and symantics to have just one implementation. So there are
# two parallel implementations, multiplexed here.

import sys
if sys.version >= '3':
    from ne3 import named_entities, encode_ampersands
else:
    from ne2 import named_entities, encode_ampersands


def test_named_entities():
    """Give it a run."""
    
    num_html   = " this &#x2014;is&#8212;an&mdash; ok?"
    named_html = " this &mdash;is&mdash;an&mdash; ok?"
   
    assert named_html == named_entities(num_html)
  
  
if __name__ == '__main__':
    test_named_entities()
