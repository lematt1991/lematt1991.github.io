#!/usr/bin/env python3

from bs4 import BeautifulSoup
import pdb, os, glob, re, datetime
import xml.etree.ElementTree as ET
import re
from jinja2 import Template
import numpy as np
from ingredient_parser import parsers
from datetime import datetime


with open('templates/recipe.html', 'r') as fin:
    html_template = Template(fin.read())

    
with open('templates/recipe.md', 'r') as fin:
    md_template = Template(fin.read())


srm_pics = [f for f in glob.glob('images/SRM*.png') if '2x' not in f]
srms = np.array([int(re.search(r'\d+', srm).group(0)) for srm in srm_pics])


def get_style(t):
    style = t.find('f_r_style')
    name = style.find('f_s_name').text
    number = style.find('f_s_number').text
    letter = chr(ord('A') + int(style.find('f_s_letter').text) - 1)
    return f'{name} ({number} {letter})'

def get_image(t=None, color=None):
    if t is not None:
        min_color = float(t.find('f_s_min_color').text)
        max_color = float(t.find('f_s_max_color').text)
        color = (min_color + max_color) / 2
    return f'/images/SRM{srms[np.argmin(np.abs(srms - color))]}.png'


def format_ingredient(t):
    parser = parsers[t.name]
    return {
        'type': parser.get_type(t),
        'amount': parser.get_amount(t),
        'name': parser.get_name(t),
        'ibu_percent': parser.get_ibu_percent(t),
        'boil_time': parser.get_boil_time(t),
    }

def format_mash(t):
    amt = float(t.find('f_ms_infusion').text)
    infusion_temp = float(t.find('f_ms_infusion_temp').text)
    temp = float(t.find('f_ms_step_temp').text)
    time = float(t.find('f_ms_step_time').text)
    description = ''
    if amt > 32:
        description += f'Add {amt/32} qt of water'
    else:
        description += f'Add {amt} oz of water'
    description += f' at {infusion_temp : .2f} F'
    return {
        'name': t.find('f_ms_name').text,
        'description': description,
        'temp': temp,
        'time': f'{time} min'
    }

def parse_water_profile(wp):
    fields = {
        'f_w_ph': 'PH',
        'f_w_calcium': 'Calcium',
        'f_w_magnesium': 'Magnesium',
        'f_w_sodium': 'Sodium',
        'f_w_sulfate': 'Sulfate',
        'f_w_chloride': 'Chloride',
        'f_w_bicarb': 'Bicarbonate',
    }
    profile = []
    for k, v in fields.items():
        val = float(wp.find(k).text)
        profile.append({
            'name': v,
            'value': f'{val:.2f}ppm'    
        })
    return profile

def tohtml(recipe):
    name = recipe.find('f_r_name').text
    filename = re.sub(r'(\s|\/)+', '_', name)
    date = datetime.strptime(recipe.find('f_r_date').text, '%Y-%m-%d')
    with open(f'recipes/{filename}.html', 'w') as fout:
        water = [i for i in recipe.find('ingredients').find('data').children if i.name == 'water']
        water_profile = []
        if len(water) > 0:
            water_profile = parse_water_profile(water[0])

        fout.write(html_template.render(
            name=name,
            style=get_style(recipe),
            image=get_image(recipe),
            details={
                'Type': recipe.find('f_e_name').text,
                'Boil Time': f'{int(float(recipe.find("f_g_boil_time").text))} Minutes',
                'Date Brewed': date.strftime('%B %d, %Y'),
                'Mash Type': recipe.find('f_mh_name').text,
            },
            ingredients=[format_ingredient(i) for i in recipe.find('ingredients').find('data').children if parsers.get(i.name, None)],
            mashs=[format_mash(i) for i in recipe.find_all('mashstep')],
            water_profile=water_profile
        ))

    markdown_file = f'_posts/{date.date().isoformat()}-{filename}.md'
    # pdb.set_trace()
    with open(markdown_file, 'w') as fout:
        fout.write(md_template.render(
            title = name,
            category = get_style(recipe),
            date = date.strftime('%B %d, %Y'),
            description = recipe.find('f_r_notes').text,
            page = f'/recipes/{filename}.html'
        ))


def main():
    recipe_file = os.path.expanduser('~/Library/Application Support/BeerSmith3/Recipe.bsmx')

    if not os.path.exists(recipe_file):
        raise ValueError("Couldn't find recipe file!")

    with open(recipe_file, 'r') as fin:
        soup = BeautifulSoup(fin.read(), features="html.parser")

    recipes = [r for r in soup.find_all('recipe') if r.find('f_r_brewer').text == '']

    os.makedirs('recipes', exist_ok=True)

    for r in recipes:
        tohtml(r)



if __name__ == '__main__':
    main()



