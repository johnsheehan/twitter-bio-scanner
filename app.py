# requires simplejson, oauth2
from oauthtwitter import OAuthApi
from time import sleep
import oauth2 as oauth
import re

def main():
    # included some symbols to avoid writing more regex
    stop_words = "\,:,/,a,able,about,across,after,all,almost,also,am,among,an,and,any,are,as,at,b,be,because,been,but,by,c,can,cannot,could,dear,did,do,does,either,e,else,ever,every,f,for,from,g,get,got,h,had,has,have,he,her,hers,him,his,how,however,i,if,in,into,is,it,its,j,just,k,l,least,let,likely,m,may,me,might,most,must,my,neither,n,no,nor,not,o,of,off,often,oh,on,only,or,other,our,own,p,q,r,rather,s,said,say,says,she,should,since,so,some,t,than,that,the,their,them,then,there,these,they,this,tis,to,too,twas,u,us,v,w,wants,was,we,were,what,when,where,which,while,who,whom,why,will,with,would,x,y,yet,you,your,z".split(",")

    # setup oauth
    consumer_key = ""
    consumer_secret = ""
    token = ""
    token_secret = ""

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
    start, end = 0, 99
    bios = []
    word_count = {}
    while end < len(ids):  # TODO: will miss remainder if count % 100 != 0
        print "fetching bios %s-%s" % (start, end)
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

        for user in apiData:
            desc = user["description"]
            if desc is None: continue

            clean = re.sub(r"[^a-zA-Z0-9\#\+\.\/\\\,\-\_]", " ", desc)
            clean = re.sub(r"(\. )|(\, )|(\- )|(\.$)", " ", clean)
            clean = re.sub(r"\.+", ".", clean)
            clean = re.sub(r" +", " ", clean)
            # TODO remove , / \ : ' - when whitespace on either side
            # TODO remove , / \  when no whitespace on both sides
            clean = clean.strip()
            if len(clean) == 0: continue
            bios.append(clean)

    # write bios to a file for later processing
    bios_file = open("bios.txt", "w")
    for bio in bios:
        bios_file.write("%s\n" % bio)
    bios_file.close()

    # loop through bio array and process each bio
    print "processing bios"
    for bio in bios:
        words = bio.split()
        lower_words = map(unicode.lower, words)
        for word in lower_words:
            # exclude stop words
            if stop_words.count(word) > 0: continue
            current_count = word_count.get(word, 0)
            current_count = current_count + 1
            word_count[word] = current_count

    # print out final counts
    for w in sorted(word_count, key=word_count.get):
        print w, word_count[w]

# TODO
# count most common following word
# count most common preceding word
    
if __name__ == '__main__':
    main()