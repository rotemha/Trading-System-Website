# from spellchecker import Spellchecker
#
# spell = Spellchecker()
#
#
#
# class SpellCheckerSystem():
# 	spell = Spellchecker()
#
# 	def correct_word(word_):
# 		word_arr = [word_]
# 		result = []
# 		misspelled = spell.unknown(word_arr)
# 		for word in misspelled:
# 			result.append(spell.correction(word))
# 		if result[0] == None:
# 			result[0] = word_
# 		return result[0]
#
# #
# # # find those words that may be misspelled
# # misspelled = spell.unknown(['let', 'us', 'wlak', 'on', 'the', 'groun'])
# #
# # for word in misspelled:
# # 	# Get the one `most likely` answer
# # 	print(spell.correction(word))
# #
# # 	# Get a list of `likely` options
# # 	print(spell.candidates(word))
