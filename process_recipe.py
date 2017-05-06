#!/usr/bin/env python

from bs4 import BeautifulSoup
import pdb, os, glob, re, datetime



for file in glob.glob('_posts/recipes/*.html'):
	now = datetime.datetime.now()
	basename = os.path.splitext(os.path.basename(file))[0]
	newFilename = '_posts/recipes/%d-%d-%d-%s.md' % (now.year, now.month, now.day, basename)

	soup = BeautifulSoup(open(file).read(), "html.parser")
	title = soup.find('title').text
	bjcpCat = soup.find('div', 'logo').find('h2').text

	date = None

	col2 = soup.find('div', 'col2').text.split('\n')
	for row in col2:
		res = re.search('Date: (.*)', row)
		if res:
			date = res.group(1)

	if date is None:
		raise Error('Could not find date!')

	notes = soup.find('h3', text="Notes").parent.text.strip().replace('\n', ' ')
	res = re.search('Notes(.*)', notes)
	short_description = res.group(1)

	newFile = open(newFilename, 'w')

	newFile.write('---\n')
	newFile.write('title: %s\n' % title)
	newFile.write('bjcp_cat: %s\n' % bjcpCat)
	newFile.write('brew_date: %s\n' % date)
	newFile.write('type: homebrew_recipe\n')
	newFile.write('short_description: %s\n' % short_description)
	newFile.write('---\n')



