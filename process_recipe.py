#!/usr/bin/env python

from bs4 import BeautifulSoup
import pdb, os, glob, re, datetime
from shutil import copyfile


for file in glob.glob('raw_recipes/*.html'):
	soup = BeautifulSoup(open(file).read(), "html.parser")
	title = soup.find('title').text.strip()
	bjcpCat = soup.find('div', 'logo').find('h2').text.strip()

	col2 = soup.find('div', 'col2')
	date = col2.find(text=re.compile("[0-9]{2} [a-zA-Z]{3} [0-9]{4}")).strip()
	date = datetime.datetime.strptime(date, "%d %b %Y")

	notes = soup.find('h3', text=re.compile(" *Notes *")).parent.text.strip().replace('\n', ' ')
	res = re.search('Notes(.*)', notes)
	short_description = res.group(1).strip()

	img = soup.find('div', 'glass').find('img')
	newImg = 'images/%s' % os.path.basename(img['src'])

	if not(os.path.exists(newImg)):
		print('Copying %s to %s' % (img['src'], newImg))
		copyfile(img['src'], newImg)
	img['src'] = '/%s' % newImg	

	basename = os.path.basename(file)
	newBasename = re.sub('( |\:)+', '-', basename)

	newHTMLFile = open('recipes/%s' % newBasename, 'w')
	newHTMLFile.write('---\nlayout: landing\n---\n')
	newHTMLFile.write('<section id="recipe" class="wrapper style3 special">\n')
	newHTMLFile.write('<div class="inner">\n')
	newHTMLFile.write(soup.find('div', {'id' : 'wrapper'}).prettify())
	newHTMLFile.write('</section>\n</div>\n')

	markdownFilename = '_posts/%d-%d-%d-%s.md' % (date.year, date.month, date.day, os.path.splitext(newBasename)[0])

	newFile = open(markdownFilename, 'w')

	newFile.write('---\n')
	newFile.write('title: %s\n' % title)
	newFile.write('bjcp_cat: %s\n' % bjcpCat)
	newFile.write('brew_date: %s\n' % date.strftime("%d, %b %Y"))
	newFile.write('type: homebrew_recipe\n')
	newFile.write('short_description: %s\n' % short_description)
	newFile.write('page_url: %s\n' % '/recipes/%s' % newBasename)
	newFile.write('---\n')



