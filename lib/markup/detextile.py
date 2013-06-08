# encoding: utf-8
from HTMLParser import HTMLParser
import urllib2

markup_map = {
  'em':     '_',
  'i':      '__',
  'strong': '*',
  'b':      '**',
  'cite':   '??',
  'del':    '-',
  'ins':    '+',
  'sup':    '^',
  'sub':    '~',
  'span':   '%'
}

align_map = {
  'left':     '<',
  'right':    '>',
  'center':   '=',
  'justify':  '<>'
}

class TextileGenerator(HTMLParser):
  def __init__(self):
    self.reset()
    self.buffer = ''

  def push(self, buffer):
    self.buffer = self.buffer + buffer
  
  def handle_starttag(self, tag, attrs):
    attrs = dict(attrs)
    buffer = ''
    for attr in attrs.keys():
      if attr == 'class':
        if 'id' in attrs.keys():
          buffer = "(%s#%s)" % (attrs['class'],attrs['id'])
        else:
          buffer = "(%s)" % attrs['class']
      elif attr == 'id':
        buffer = "(#%s)" % attrs['id']
      if attr == 'style':
        buffer = buffer + "{%s}" % attrs['style']
      if attr == 'lang':
          buffer = buffer + "[%s]" % attrs['style']
      if attr == 'align':
        try:
          buffer = buffer + attrs['align']
        except:
          pass
      
    self.handle_common(tag)
    if tag == 'blockquote':
      self.push('bq. ')
    # simple list handling
    if tag in ['ol','ul']:
      self.listtype = tag
    if tag == 'li':
      if self.listtype == 'ol':
        self.push('# ')
      elif self.listtype == 'ul':
        self.push('* ')
    if tag in ['h1','h2','h3','h4','p']:
      self.push(tag + buffer + '. ')  

  def handle_data(self, text):
    self.push(text)
  
  def handle_common(self, tag):
    try:
      self.push(markup_map[tag])
    except:
      pass
  
  def handle_endtag(self, tag):
    self.handle_common(tag)
  

if __name__ == '__main__':
  stream = urllib2.urlopen('http://pfig.livejournal.com')
  buffer = stream.read()
  p = TextileGenerator()
  p.feed(buffer)
  print p.buffer