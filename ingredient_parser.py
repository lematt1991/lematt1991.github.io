import pdb

class IngredientParser:
	def get_type(self, t):
		return t.name.capitalize()

	def get_name(self, t):
		return t.find(f'{self.prefix}_name').text

	def get_amount(self, t):
		amount = float(t.find(f'{self.prefix}_amount').text)
		if amount > 16:
			pounds = int(amount / 16)
			ounces = amount % 16
			if ounces == 0:
				return f'{pounds} lbs'
			else:
				return f'{pounds} lbs {ounces} oz'
		return f'{amount} oz'

	def get_ibu_percent(self, t):
		return '-'

	def get_boil_time(self, t):
		return '-'

class HopParser(IngredientParser):
	prefix = 'f_h'

	def get_ibu_percent(self, t):
		amt = float(t.find('f_h_ibu_contrib').text)
		return f'{amt:.1f} IBUs'

	def get_boil_time(self, t):
		use = int(t.find('f_h_use').text)
		amt = int(float(t.find('f_h_boil_time').text))
		if use == 1:
			return 'Dry Hop'
		else:
			return f'{amt} min'

class GrainParser(IngredientParser):
	prefix = 'f_g'

	def get_ibu_percent(self, t):
		amt = float(t.find('f_g_percent').text)
		return f'{amt:.1f} %'

class YeastParser(IngredientParser):
	prefix = 'f_y'

	def get_amount(self, t):
		amount = float(t.find(f'{self.prefix}_amount').text)
		return f'{amount} pkg'

parsers = {
	'hops': HopParser(),
	'grain': GrainParser(),
	'yeast': YeastParser()
}