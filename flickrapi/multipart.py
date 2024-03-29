# -*- encoding: utf-8 -*-

'''Module for encoding data as form-data/multipart'''

import os
import base64
import random
import md5

class Part(object):
    '''A single part of the multipart data.
    
    >>> #doctest: +ELLIPSIS
    >>> Part({'name': 'headline'}, 'Nice Photo') 
    <flickrapi.multipart.Part object at 0x...>
    
    >>> image = file('tests/photo.jpg')
    >>> Part({'name': 'photo', 'filename': image}, image.read(), 'image/jpeg')
    <flickrapi.multipart.Part object at 0x...>
    '''
    
    def __init__(self, parameters, payload, content_type=None):
        self.content_type = content_type
        self.parameters = parameters
        self.payload = payload

    def render(self):
        '''Renders this part -> List of Strings'''
        
        parameters = ['%s="%s"' % (k, v) for k, v in self.parameters.iteritems()]
        
        lines = ['Content-Disposition: form-data; %s' % '; '.join(parameters)]
        
        if self.content_type:
            lines.append("Content-Type: %s" % self.content_type)
        
        lines.append('')
        
        if isinstance(self.payload, unicode):
            lines.append(self.payload.encode('utf-8'))
        else:
            lines.append(self.payload)
        
        return lines

class FilePart(Part):
    '''A single part with a file as the payload
    
    This example has the same semantics as the second Part example:

    >>> #doctest: +ELLIPSIS
    >>> FilePart({'name': 'photo'}, 'tests/photo.jpg', 'image/jpeg')
    '''
    
    def __init__(self, parameters, filename, content_type):
        parameters['filename'] = filename
        
        imagefile = open(filename, 'rb')
        payload = imagefile.read()
        imagefile.close()

        Part.__init__(self, parameters, payload, content_type)

def boundary():
    """Generate a random boundary, a bit like Python 2.5's uuid module."""

    #bytes = os.urandom(16)
    m = md5.new()
    m.update("something")
    m.update(str(random.randint(0, 100000)))
    bytes = m.hexdigest()
    
    return bytes[1:16] #base64.b64encode(bytes, 'ab').strip('=')
   
class Multipart(object):
    '''Container for multipart data'''
    
    def __init__(self):
        '''Creates a new Multipart.'''
        
        self.parts = []
        self.content_type = 'form-data/multipart'
        self.boundary = boundary()
        
    def attach(self, part):
        '''Attaches a part'''
        
        self.parts.append(part)
    
    def __str__(self):
        '''Renders the Multipart'''

        lines = []
        for part in self.parts:
            lines += ['--' + self.boundary]
            lines += part.render()
        lines += ['--' + self.boundary.encode('utf-8') + "--"]

        out = ''
        for s in lines:
            out += str(s) + '\r\n'
        #r = '\r\n'.join(lines)
        #NSLog("test -- ok")
        return out
    
    def header(self):
        '''Returns the top-level HTTP header of this multipart'''
        
        return ("Content-Type", "multipart/form-data; boundary=%s" % self.boundary)
