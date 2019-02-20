#!/usr/bin/env python

from subprocess import Popen, PIPE
import os, sys, re, codecs
from bs4 import BeautifulSoup, NavigableString, Tag
import copy

folder = sys.argv[2]
filename = sys.argv[1]

# convert doc to html
convertHTML = Popen(["pandoc", "--extract-media=" + folder, "--to=html", filename], stdout=PIPE)

htmlDoc = convertHTML.communicate()[0].decode('utf-8')

soup = BeautifulSoup(htmlDoc, 'html.parser')

# get footnotes and remove footnote-div
footnotes = soup.find_all("section", class_="footnotes")

if len(footnotes) > 0:
    footnotes = footnotes[0].extract().find_all("li")
    footnotes = [[note.get('id'), note.getText()[:-1]] for note in footnotes]
    fnLinks = soup.find_all("a", class_="footnote-ref")
    # replace footnote links with RC footnote links
    idx = 0
    for link in fnLinks:
        del(link['id'])
        del(link['class'])
        link['href'] = "#"
        # popover is missing (number)
        link['data-popover-options'] = u"{{\"title\":\"{}\", \"creation_type\":\"text\", \"text\":\"{}\",\"viewon\":\"0\", \"postion\":\"1\", \"background\":\"0\", \"changed\":true, \"autocontent\": true}}".format(u"footnote{}".format(idx+1), footnotes[idx][1])
        link['data-popover-auto'] = "1"
        link.string = "x"
        idx += 1

        
# split by h2, size and img
content = soup.contents
pages = []
thispage = []
imgidxs = []
imgfiles = []
pagesidxs = []
counter = 0
for el in content:
    if (isinstance(el, Tag)):
        images = el.find_all('img') + el.find_all('embed')
        if len(images) > 0:
            if len(thispage) > 0:
                pages.append(''.join(thispage))
                pagesidxs.append(counter)
                counter += 1
                thispage = []
            for img in images:
                imgfiles.append(img['src'])
                imgidxs.append(counter)
                counter += 1
               # print(el)
                img.extract()
               # print(el)
    if (el.name == 'h1') or  (el.name == 'h2') or (len(''.join(thispage)) > 4000):
        if (len(thispage) > 0) and (not ''.join(thispage).isspace()):
            pages.append(''.join(thispage))
            pagesidxs.append(counter)
            counter += 1
            thispage = [unicode(el)]
        else:
            thispage.append(unicode(el))
    else:
        thispage.append(unicode(el))
pages.append('\n'.join(thispage))
pagesidxs.append(counter)

if not os.path.isdir(folder):
    os.mkdir(folder)

# write text sections to html files
for idx,section in enumerate(pages):
    sectionId = "section" + '{0:04d}'.format(pagesidxs[idx]+1)
    filename = '{0:04d}'.format(pagesidxs[idx]+1) + ".html"
    fileOut = codecs.open(os.path.join(folder, filename), "w",  encoding='utf-8')
    sectionString = '<div class="rc-html-reset" id="{id}">{section}</div>'.format(id=sectionId, section=section)
    fileOut.write(sectionString)
    fileOut.close()

# sort image files by numbers in filename
#imageFiles = os.listdir(os.path.join(folder, "media"))
#imageFiles.sort(key=lambda f: int(filter(str.isdigit, f)))

# move files to outer dir and rename to right number
for idx,f in enumerate(imgfiles):
    filename, file_extension = os.path.splitext(f)
    os.rename(f, os.path.join(folder, '{0:04d}'.format(imgidxs[idx]+1) + file_extension))

# remove "media" dir if it exists
mediaDir = os.path.join(folder, "media")
if os.path.isdir(mediaDir):
    os.rmdir(mediaDir)

    


