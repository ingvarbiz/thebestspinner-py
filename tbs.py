import re
import urllib2
import urllib
from xml.dom import minidom


class Error(Exception):
    """Base class for exceptions in this module."""
    pass


class AuthenticationError(Error):
    """
    Raised when authentication error encountered
    """
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __str__(self):
        return "Could not authenticate with username: %s and password: %s." % (self.username, self.password)
    
    
class QuotaUsedError(Error):
    """
    Raised when API quota limit reached (250 queries per day)
    """
    def __str__(self):
        return "The Best Spinner API query limit has been reached for today (250 queries per day)."
    

class Api(object):
    """
    A class to use The Best Spinner api (get an account at http://snurl.com/the-best-spinner) 
    """
    def __init__(self, username, password, quotalimit = 250):
        self.url = 'http://thebestspinner.com/api.php'
        self.username = username
        self.password = password
        self.quotalimit = quotalimit
        self.authenticated = False
        self.token = ''

    def _authenticate(self):
        """
        Gets and stores session identifier to be used for each subequent request
        """
        if self.authenticated:
            return

        data = (
            ('action', 'authenticate'),
            ('format', 'xml'),
            ('username', self.username),
            ('password', self.password),
        )
        con = urllib2.urlopen(self.url, urllib.urlencode(data))
        
        xml = con.read()
        dom = minidom.parseString(xml)
        
        if self._getText(dom.getElementsByTagName('success')[0]) == 'true':
            self.authenticated = True
            self.token = self._getText(dom.getElementsByTagName('session')[0])
        else:
            raise AuthenticationError(self.username, self.password)
            
        
    def identifySynonyms(self, text, max_syns=3, phrases=()):
        """
        Calls the 'identitySynonyms' api function (counts towards api query quota). Returns spin-formatted text,
        identified synonyms are replaced.
        
        Args:
            text (str): The text to perform the synonym identification on (max 5,000 words).

        Kwargs:
            max_syns (int): The maximum number of synonyms to return for a word/phrase, default 3.
            phrases (tuple or list): Phrases/words in text that should not be altered and synonyms not sought.
        """
        if not self.authenticated:
            self._authenticate()
        
        text = self._replacePhrases(text, phrases)
        data = (
            ('action', 'identifySynonyms'),
            ('format', 'xml'),
            ('session', self.token),
            ('text', text.encode('utf-8')),
            ('maxsyns', max_syns),
        )
        con = urllib2.urlopen(self.url, urllib.urlencode(data))
        xml = con.read()
        dom = minidom.parseString(xml)
        
        if self._getText(dom.getElementsByTagName('success')[0]) == 'true':
            output = self._getText(dom.getElementsByTagName('output')[0]).replace('\\','')
            return self._replacePlaceholders(output, phrases)
                
        else:
            if self.apiQuota() <= 250:
                raise QuotaUsedError()
            else:
                raise Exception("identifySynonyms failed, reason unknown")


    def replaceEveryonesFavorites(self, text, max_syns=3, quality=3, phrases=()):
        """
        Calls the 'replaceEveryonesFavorites' api function (counts towards api query quota). Returns spin-formatted text
        with 'everyone's favorites' replaced. 
        
        Args:
            text (str): The text to perform the synonym identification on (max 5,000 words).

        Kwargs:
            max_syns (int): The maximum number of synonyms to return for a word/phrase, default 3.
            quality (int): 1 = Good, 2 = Better, 3 = Best.
            phrases (tuple or list): Phrases/words in text that should not be altered and synonyms not sought.
        """
        if not self.authenticated:
            self._authenticate()
            
        text = self._replacePhrases(text, phrases)
        
        data = (
            ('action', 'replaceEveryonesFavorites'),
            ('format', 'xml'),
            ('session', self.token),
            ('text', text.encode('utf-8')),
            ('maxsyns', max_syns),
            ('quality', quality),
        )
        con = urllib2.urlopen(self.url, urllib.urlencode(data))
        xml = con.read()
        dom = minidom.parseString(xml)
        
        if self._getText(dom.getElementsByTagName('success')[0]) == 'true':
            output = self._getText(dom.getElementsByTagName('output')[0]).replace('\\','') 
            return self._replacePlaceholders(output, phrases)
                
        else:
            if self.apiQuota() <= 250:
                raise QuotaUsedError()
            else:
                raise Exception("replaceEveryonesFavorites failed, reason unknown")
   

    def randomSpin(self, text, phrases=()):
        """
        Calls the 'randomSpin' api function, returns a spun version of the spin-formatted text provided.
        
        Args:
            text (str): Spin-formatted text to return a randomly spun version of (max 5,000 words).

        Kwargs:
            phrases (tuple or list): Phrases/words in text that should not be altered and synonyms not sought.
        """
        if not self.authenticated:
            self._authenticate()
        
        text = self._replacePhrases(text, phrases)
        data = (
            ('action', 'randomSpin'),
            ('format', 'xml'),
            ('session', self.token),
            ('text', text.encode('utf-8')),
        )
        con = urllib2.urlopen(self.url, urllib.urlencode(data))
        xml = con.read()
        dom = minidom.parseString(xml)
        
        if self._getText(dom.getElementsByTagName('success')[0]) == 'true':
            output = self._getText(dom.getElementsByTagName('output')[0]).replace('\\','') 
            return self._replacePlaceholders(output, phrases)
                
        else:
            if self.apiQuota() <= 250:
                raise QuotaUsedError()
            else:
                raise Exception("randomSpin failed, reason unknown")

    def apiQuota(self):
        """
        Returns the number of queries allowed to perform today
        """
        queries_today = self.apiQueries()
        queries_allowed = self.quotalimit - queries_today
        if queries_allowed < 0:
            quesries_allowed = 0
        return queries_allowed
        
    def apiQueries(self):
        """
        Returns the number of api requests made today (the api has a limit of 250 per day).
        """ 
        if not self.authenticated:
            self._authenticate()
        
        data = (
            ('action', 'apiQueries'),
            ('format', 'xml'),
            ('session', self.token),
        )
        con = urllib2.urlopen(self.url, urllib.urlencode(data))
        xml = con.read()
        dom = minidom.parseString(xml)
        
        if self._getText(dom.getElementsByTagName('success')[0]) == 'true':
            return int(self._getText(dom.getElementsByTagName('output')[0]))

        else:
            raise Exception("apiQueries failed, reason unknown")
   

    def _getText(self, node):
        """ 
        Takes a DOM Element and returns its text.
        Makes working with xml.dom.minidom easier, should really be part of that package
        """
        return node.firstChild.nodeValue

    
    def _replacePhrases(self, text, phrases):
        """
        A utility method to replace words/phrases that shouldn't be identified as synonyms with a placeholder.
        @param text: Text in which to replace words/phrases.
        @param phrases: a tuple or list of phrases to replace (a phrase can be one or more words eg 'cat' and 'a dog')
        """
        for i, phrase in enumerate(phrases):
            for match in re.finditer(r'\b(%s)\b' % phrase, text):
                text = text[:match.start(1)] + '~%d~' % i + text[match.end(1):] 

        return text
    
    
    def _replacePlaceholders(self, text, phrases):
        """
        A utility method to replace placeholders with the original words/phrases that were switched with _replacePhrases
        @param text: Text in which to unmark words/phrases.
        @param phrases: the same tuple or list that was passed to _replacePhrases()
        """
        for i, phrase in enumerate(phrases):
            text = text.replace('~%d~' % i, phrases[i])
            
        return text
    

