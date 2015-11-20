from mrjob.job import MRJob
from mrjob.step import MRStep
from scipy.stats.stats import pearsonr

class MRCalculateSimilarity(MRJob):

	def steps(self):
		return [
            MRStep(mapper=self.mapper_user_id_key,
                   reducer=self.reducer_artist_pairs),
			MRStep(reducer=self.reducer_artist_similarities)
		]

	def mapper_user_id_key(self, _, line):
		#Note we're assuming csv here
		user_id, artist_id, log_listens, user_average = line.split(',')
		yield (user_id, (artist_id, log_listens, user_average))

	def reducer_artist_pairs(self, user_id, rows):
		rows = list(rows)
		#Since we are looking at one user in each reduce, the artist_ids will all be unique
		artist_ids = [x[0] for x in rows]
		user_average = float(rows[0][2])

		for i, artist_i in enumerate(artist_ids):
			for j, artist_j in enumerate(artist_ids):
				#String comparison
				if artist_i < artist_j:
					i_ll = float(rows[i][1])
					j_ll = float(rows[j][1])
					#Do the average subtractions here to avoid passing them to the next step
					yield ((artist_i, artist_j), (i_ll-user_average, j_ll-user_average))

	#"Null mapper"

	def reducer_artist_similarities(self, artist_pair, rating_pairs):
		rating_pairs = list(rating_pairs)
		#If only one rating pair, pearsonr is NaN. To avoid this,
		if(len(rating_pairs) > 1):
			#But if len is 2, then pearsonr is either 1 or -1
			artist1_ll_minus_ave = [float(x[0]) for x in rating_pairs]
			artist2_ll_minus_ave = [float(x[1]) for x in rating_pairs]
			#Apply-regularization-later version:
			yield (artist_pair, (pearsonr(artist1_ll_minus_ave, artist2_ll_minus_ave)[0], len(rating_pairs)))

if __name__ == '__main__':
	MRCalculateSimilarity.run()
