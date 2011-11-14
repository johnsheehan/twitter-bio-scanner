# requires simplejson, oauth2
from oauthtwitter import OAuthApi
from optparse import OptionParser
from time import sleep
from config import oauth_config
import codecs
import oauth2 as oauth
import re

bios = []
word_count = {}

def main():
    # parse command line options
    parser = OptionParser()
    parser.add_option("-s", "--source", dest="source",
                      help="if specified, use source file name")
    (options, args) = parser.parse_args()

    if options.source:
        print "reading from %s" % options.source
        with codecs.open(options.source, encoding="utf-8", mode="r") as bios_file:
            bios.extend(map(unicode, bios_file.readlines()))

        parse_bios()
    else:
        print "fetching from twitter"
        fetch_and_store()
        parse_bios()

# TODO
# count most common following word
# count most common preceding word

def parse_bios():
    # loop through bio array and process each bio
    print "processing %i bios" % len(bios)

    # included some symbols to avoid writing more regex
    stop_words = "0,1,2,3,4,5,6,7,8,9,_,+,&,@,.,\,:,/,a,able,about,across,after,all,almost,also,am,among,an,and,any,are,as,at,b,be,because,been,but,by,c,can,cannot,could,d,de,dear,did,do,does,either,e,else,ever,every,f,for,from,g,get,got,h,had,has,have,he,her,hers,him,his,how,however,i,if,in,into,is,it,its,j,just,k,l,least,let,likely,m,may,me,might,most,must,my,neither,n,no,nor,not,o,of,off,often,oh,on,only,or,other,our,own,p,q,r,rather,s,said,say,says,she,should,since,so,some,t,than,that,the,their,them,then,there,these,they,this,tis,to,too,twas,u,us,v,w,wants,was,we,were,what,when,where,which,while,who,whom,why,will,with,would,x,y,yet,you,your,z".split(",")

    for bio in bios:
        clean = re.sub(ur"[^a-zA-Z0-9\#\+\.\/\,\-\_\&\:\?]", r" ", bio)
        clean = re.sub(ur"(\.|\,|\-)\s", r" ", clean)
        clean = re.sub(ur"\S+$", r"", clean)
        clean = re.sub(ur"(\.|\,|\s)+", r"\1", clean)
 
        # TODO remove , / \ : ' & - when whitespace on either side
        # TODO remove , \  when no whitespace on both sides
        clean = clean.strip()
        if len(clean) == 0: continue

        words = clean.split()
        lower_words = map(unicode.lower, words)
        for word in lower_words:
            # exclude stop words
            if word in stop_words: continue
            word_count[word] = word_count.get(word, 0) + 1

    # print out final counts
    with codecs.open("results.txt", encoding="utf-8", mode="w") as results_file:
        for w in sorted(word_count, key=word_count.get):
            print w, word_count[w]
            results_file.write("%s %s\n" % (w, word_count[w]))


def fetch_and_store():
    # setup oauth
    consumer_key    = oauth_config["consumer_key"]
    consumer_secret = oauth_config["consumer_secret"]
    token           = oauth_config["token"]
    token_secret    = oauth_config["token_secret"]

    # retreive followers
    twitter = OAuthApi(consumer_key, consumer_secret, token, token_secret)

    #returns a dict formatted from the JSON data returned
    cursor = -1;
    ids = []
    while cursor != 0:
        apiData = twitter.ApiCall("followers/ids", "GET", { 'cursor' : cursor })

        print "returned:    %s" % len(apiData["ids"])
        print "next_cursor: %s" % apiData["next_cursor"]

        ids.extend(apiData["ids"])
        cursor = apiData["next_cursor"]

    print "followers:   %s" % len(ids) 

    # put bios into array
    # have to retrieve them 100 at a time from twitter
    start, end = 0, 100
    total = len(ids)

    with codecs.open("bios.txt", encoding="utf-8", mode="w") as bios_file:
        while start < total:
            print "fetching bios %s-%s" % (start+1, end)
            current = ids[start:end]

            id_list = ",".join(map(str, current))
            try:
                apiData = twitter.ApiCall("users/lookup", "GET", { 'user_id' : id_list })
            except:
                print "error! sleeping..."
                sleep(5)
                continue

            # only advance counts if http succeeds
            start = start + 100
            end = end + 100

            # write bios to a file for later processing
            for user in apiData:
                desc = user["description"].strip()
                if desc is None: continue
                bios_file.write("%s\n" % desc)
                bios.append(desc)
    
if __name__ == '__main__':
    main()