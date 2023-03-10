import datetime
import feedparser
import os
import re
import time
import yaml

def load_rss():
    d = feedparser.parse('./libsyn-legacy/rss')
    return d

def timestruct_to_isoformat(ts):
    t = time.mktime(ts)
    dt = datetime.datetime.fromtimestamp(t)
    iso = dt.isoformat()
    return iso

def gimme_mp3(links):
    yolo=None
    for link in links:
        href = link['href']
        if href.endswith('.mp3'):
            return href
        else:
            yolo = href
    return yolo

def line_break_text(text):
    out=""
    lines = text.split("\n")
    for line in lines:
        if " " not in line:
            out = out + line + "\n"
            continue
        if len(line) < 100:
            out = out + line + "\n"
            continue
        try:
            index = line.index(" ", 80)
        except ValueError as ve:
            out = out + line + "\n"
            continue
        a = line[:index].strip(' ')
        b = line[index:].strip(' ')
        out = out + a + "\n"
        out = out + line_break_text(b)
    return out

def libsyn_to_markdown(text):
    text = re.sub("<[/]*p>", "", text)
    text = re.sub('<a href="([^"]+)">([^<]+)</a>', r"[\2](\1)", text)
    text = line_break_text( text )
    return text

# Extremly specific check for our puproses.
# Older than November 2021, we don't care
def ancient(st):
    value = st.tm_year * 100 + st.tm_mon
    if value <= 202111:
        return True
    return False

def generate_filename(title):
    fn = title
    fn = fn.lower()
    fn = fn.replace('å','a')
    fn = fn.replace('ä','a')
    fn = fn.replace('ö','o')
    fn = re.sub('[^a-zA-Z0-9]+', '_', fn)
    fn = fn.strip('_')
    fn = fn + ".md"
    return fn

def mkdir(p):
    if not os.path.exists(p):
        os.makedirs(p)

def process_entry(e):
    published_p  = e['published_parsed']
    if ancient(published_p):
        return
    title        = e['title']
    summary      = e['summary']
    duration     = e['itunes_duration']
    links        = e['links']
    published_pp  = timestruct_to_isoformat( published_p )
    mp3 = gimme_mp3(links)

    fdir = "../www-hugo/content/posts"
    mkdir(fdir)

    fname = generate_filename(title)
    with open(fdir + "/" + fname, "w") as f:
        header = {}
        header['title'] = title
        header['date'] = published_pp
        header_yaml = yaml.dump(header)
        md_content = libsyn_to_markdown(summary)
        f.write("---\n")
        f.write(header_yaml)
        f.write("---\n")
        f.write("## Lyssna\n")
        f.write(f"* [mp3]({mp3}), längd: {duration}\n\n")
        f.write("## Innehåll\n")
        f.write(md_content)

def main():
    rss = load_rss()
    entries = rss['entries'];
    for entry in entries:
        process_entry(entry)

if __name__ == "__main__":
    main()
