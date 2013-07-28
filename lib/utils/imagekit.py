#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Image utilities

Created by: Rui Carmo
License: MIT (see LICENSE for details)
"""

def get_info(data):
    """Parses a small buffer and attempts to return basic image metadata"""
    
    data = str(data)
    size = len(data)
    height = -1
    width = -1
    content_type = ''

    # handle GIFs
    if (size >= 10) and data[:6] in ('GIF87a', 'GIF89a'):
        # Check to see if content_type is correct
        content_type = 'image/gif'
        w, h = struct.unpack("<HH", data[6:10])
        width = int(w)
        height = int(h)

    # See PNG 2. Edition spec (http://www.w3.org/TR/PNG/)
    # Bytes 0-7 are below, 4-byte chunk length, then 'IHDR'
    # and finally the 4-byte width, height
    elif ((size >= 24) and data.startswith('\211PNG\r\n\032\n')
          and (data[12:16] == 'IHDR')):
        content_type = 'image/png'
        w, h = struct.unpack(">LL", data[16:24])
        width = int(w)
        height = int(h)

    # Maybe this is for an older PNG version.
    elif (size >= 16) and data.startswith('\211PNG\r\n\032\n'):
        # Check to see if we have the right content type
        content_type = 'image/png'
        w, h = struct.unpack(">LL", data[8:16])
        width = int(w)
        height = int(h)

    # Check for a JPEG
    elif (size >= 4):                                                          
        jpeg = StringIO.StringIO(data)                                         
        b = jpeg.read(4)                                                       
        if b.startswith('\xff\xd8\xff\xe0'):                                   
            content_type = 'image/jpeg'                                        
            bs = jpeg.tell()                                                   
            b = jpeg.read(2)                                                   
            bl = (ord(b[0]) << 8) + ord(b[1])                                  
            b = jpeg.read(4)                                                   
            if b.startswith("JFIF"):                                           
                bs += bl                                                       
                while(bs < len(data)):                                         
                    jpeg.seek(bs)                                              
                    b = jpeg.read(4)                                           
                    bl = (ord(b[2]) << 8) + ord(b[3])                          
                    if bl >= 7 and b[0] == '\xff' and b[1] == '\xc0':          
                        jpeg.read(1)                                           
                        b = jpeg.read(4)                                       
                        height = (ord(b[0]) << 8) + ord(b[1])                  
                        width = (ord(b[2]) << 8) + ord(b[3])                   
                        break                                                  
                    bs = bs + bl + 2      
    return width, height, content_type  