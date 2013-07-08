#!/usr/bin/env python
# encoding: utf-8

"""
Assets.py

Created by Rui Carmo on 2012-04-19.
Published under the MIT license.
"""

from snakeserver.snakelet import Snakelet
import os, sys, time, rfc822, unittest, urlparse, urllib, re, stat, cgi
import fetch, simplejson, codecs
from BeautifulSoup import BeautifulSoup, BeautifulStoneSoup
from yaki.Page import Page
from yaki.Store import Store
from yaki.Utils import *
from yaki.Layout import *
import yaki.Plugins
from yaki.Locale import *

# try to speed up pickle if possible
try:
    import cPickle as pickle
except ImportError: # fall back on Python version
    import pickle 


class WikiAttachment(Snakelet):
    """
    File attachment server (currently spits out files placed alongside the index document on the filesystem)
    """
    def getDescription(self):
        return "Wiki Attachment Locator"
    
    def allowCaching(self):
        return True
    
    def requiresSession(self):
        return self.SESSION_DONTCREATE
    
    def getAttachmentFilename(self, request):
        a = request.getWebApp()
        c = request.getContext()
        c.fullurl = request.getBaseURL() + request.getFullQueryArgs()
        path = urllib.unquote((request.getPathInfo())[1:])
        (page,attachment) = os.path.split(path)
        ac = a.getContext()
        # TODO: change this to allow for retrieving a file handle from Store
        # ...and caching the data into a Haystack
        filename = ac.store.getAttachmentFilename(page,attachment)
        return filename
    
    def setHeaders(self, request, response, filename = None, stats = None):
        a = request.getWebApp()
        try:
            if filename:
                stats = os.stat(filename)
                (mtime, size, ino) = (stats.st_mtime, stats.st_size, stats.st_ino)
            else:
                (mtime, size, ino) = (stats[0], stats[1], stats[2])
            (etag,lmod) = a.create_ETag_LMod_headers(mtime, size, ino)
            response.setHeader("Last-Modified", lmod)
            response.setHeader("Etag", etag)
        except Exception, e:
            print "Error sending headers: %s" % e
            pass
        # Most caching testing tools are stupid enough to work with a one-year threshold 
        # to test for "cacheability".
        # I decided to humor them, hence the figure below
        response.setHeader("Cache-Control",'max-age=34560000')
        response.setHeader("Expires", httpTime(time.time() + 34560000))
    
    def serve(self, request, response):
        request.setEncoding("UTF-8")
        response.setEncoding("UTF-8")
        a = request.getWebApp()
        filename = self.getAttachmentFilename(request)
        if os.path.exists(filename) and not os.path.isdir(filename):
            self.setHeaders(request, response, filename)
            a.serveStaticFile(filename, response, useResponseHeaders=False)
            return
        response.setResponse(404, "Not Found")
        return
    

class FontPreview(WikiAttachment):
  """
  Font preview server - requires ImageMagick
  """
  def getDescription(self):
      return "Font preview generator"
  
  def doFontMagick(self, filename):
    # TODO: fix this for filenames with quotation marks.
    return os.popen("""convert -font "%s" -size 1024x800 -resize 50%% -gravity center -quality 95 -background white label:'ABCDEFGHIJKLM\\nNOPQRSTUVWXYZ\\nabcdefghijklm\\nnopqrstuvwxyz\\n1234567890' jpeg:-""" % filename, "rb").read()

  def serve(self, request, response):
    request.setEncoding("UTF-8")
    response.setEncoding("UTF-8")
    ac = request.getWebApp().getContext()
    filename = self.getAttachmentFilename(request)
    buffer = ''
    # blindly assume we'll only try to do this for valid font files - i.e., no bytestream checks
    if os.path.exists(filename) and not os.path.isdir(filename):
      try:
        stats = ac.cache.stats("fpreview:%s" % filename)
        buffer = ac.cache["fpreview:%s" % filename]
      except KeyError:
        if os.path.splitext(filename)[1] in ['.ttf','.otf']:
          buffer = self.doFontMagick(filename)
        if buffer == '': 
          response.setResponse(404, "Not Found")
          return
        ac.cache["fpreview:%s" % filename] = buffer
        stats = ac.cache.stats("fpreview:%s" % filename)
      self.setHeaders(request, response, stats = stats)
      response.setContentType("image/jpeg")
      response.setHeader("X-Generator", "ImageMagick-FontPreview")
      response.setEncoding(None)
      response.getOutput().write(buffer)
      return
    response.setResponse(404, "Not Found")
    return


class AdaptiveImage(WikiAttachment):
    """
    AdaptiveImage server - requires ImageMagick and does not (by design) allow for any sort of parameters
    """
    def getDescription(self):
        return "Adaptive image resizer"
        
    def doImageMagick(self, filename, width=320):
        return os.popen("""convert "%s" -adaptive-resize %d -quality 75 -background white -strip -interlace Plane -flatten jpeg:-""" % (filename,width), "rb").read()
  
    def serve(self, request, response):
        sizes = [1382, 992, 768, 480]
        pixel_density = 1
        request.setEncoding("UTF-8")
        response.setEncoding("UTF-8")
        ac = request.getWebApp().getContext()
        filename = self.getAttachmentFilename(request)
        cookie = "(not found)"
        try:
            resolution = request.getCookies()['resolution'][0]
            cookie = resolution
            # check for a valid cookie
            if not re.match('^[0-9]+[,]*[0-9\.]+$',resolution):
                print "DEBUG: resetting resolution cookie."
                response.delCookie(resolution,'/')
            resolution = resolution.split(',')
            client_width = int(resolution[0])
            try:
                pixel_density = int(resolution[1])
            except:
                pass
            # now work on the final resolution
            resolution = sizes[0]
            if pixel_density != 1:
                total_width = client_width * pixel_density
                if total_width > resolution:
                    for break_point in sizes:
                        if total_width <= break_point:
                            resolution = break_point
                    resolution = resolution * pixel_density
                else:
                    for break_point in sizes:
                        if total_width <= break_point:
                            resolution = break_point
            else:
                for break_point in sizes:
                    if total_width <= break_point:
                        resolution = break_point
            print "DEBUG: resolution:", resolution
        except:
            if 'mobile' in request.getUserAgent().lower():
                resolution = min(sizes)
            else:
                resolution = max(sizes)

        # blindly assume we'll only try to do this for valid image files - no bytestream checks
        if os.path.exists(filename) and not os.path.isdir(filename):
            try:
                stats = ac.cache.stats("image:%d-%s" % (resolution,filename))
                buffer = ac.cache["image:%d-%s" % (resolution,filename)]
            except KeyError:
                # Try to read enough bytes to skip over EXIF data and inline thumbnails
                # TODO: cache this inside snakelet
                (width, height, dummy) = getImageInfo(open(filename,'r').read(65535))
                if(min(sizes) > max(width, height)):
                    # just return the image as is
                    self.setHeaders(request, response, filename)
                    request.getWebApp().serveStaticFile(filename, response, useResponseHeaders=False)
                    return
                else:
                    buffer = self.doImageMagick(filename,resolution)
                    if buffer == '':
                        response.setResponse(404, "Not Found")
                        return
                    ac.cache["image:%d-%s" % (resolution,filename)] = buffer
                    stats = ac.cache.stats("image:%d-%s" % (resolution,filename))
            # print "DEBUG: returning %s at %s/%d, %d bytes" % (filename, cookie, resolution, len(buffer))
            self.setHeaders(request, response, stats = stats)
            # We're going to return everything as JPEGs
            response.setContentType("image/jpeg")
            response.setHeader("X-Resolution", "screen: %s, image: %d" % (cookie, resolution))
            response.setHeader("X-Generator", "ImageMagick-AdaptiveResize")
            response.setEncoding(None)
            response.getOutput().write(buffer)
            return
        response.setResponse(404, "Not Found")
        return


class Thumbnail(WikiAttachment):
  """
  Image thumbnail server - requires ImageMagick and does not (by design) allow for any sort of parameters
  TODO: sanitize this and the font previewer on a second pass.
  """
  def getDescription(self):
    return "Image thumbnail generator"
    
  def doImageMagick(self, filename):
    return os.popen("""convert "%s" -thumbnail x320 -resize '320x<' -resize 50%% -gravity center -crop 160x160+0+0 +repage -quality 95 -background white -flatten jpeg:-""" % filename, "rb").read()
  
  def doFontMagick(self, filename):
    return os.popen("""convert -font "%s" -size 800x400 -thumbnail x320 -resize '320x<' -resize 50%% -gravity center -crop 160x160+0+0 +repage -quality 95 -background white -flatten label:'  Aa  ' jpeg:-""" % filename, "rb").read()
 
  def serve(self, request, response):
    request.setEncoding("UTF-8")
    response.setEncoding("UTF-8")
    ac = request.getWebApp().getContext()

    filename = self.getAttachmentFilename(request)

    # blindly assume we'll only try to do this for valid image files
    if os.path.exists(filename) and not os.path.isdir(filename):
      try:
        stats = ac.cache.stats("thumbnail:%s" % filename)
        buffer = ac.cache["thumbnail:%s" % filename]
      except KeyError:
        if os.path.splitext(filename)[1] in ['.ttf','.otf']:
          buffer = self.doFontMagick(filename)
        else:
          buffer = self.doImageMagick(filename)
        if buffer == '':
          response.setResponse(404, "Not Found")
          return
        ac.cache["thumbnail:%s" % filename] = buffer
      self.setHeaders(request, response, stats = ac.cache.stats("thumbnail:%s" % filename))
      response.setContentType("image/jpeg")
      response.setHeader("X-Generator", "ImageMagick-Thumbnail")
      response.setEncoding(None)
      response.getOutput().write(buffer)
      return
    response.setResponse(404, "Not Found")
    return


class PageThumbnail(Thumbnail):
    """
    Screenshot thumbnails
    """
    
    def getDescription(self):
        return "Page thumbnail resizer"

    def doImageMagick(self, filename):
        return os.popen("""convert "%s" -strip -thumbnail 320 -quality 95 -background white -flatten jpeg:-""" % filename, "rb").read()

