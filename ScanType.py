class ScanType:
	def __init__(self, scan_id, date_time, quality, angle, distance):
		self.scan_id = scan_id
		self.date_time = date_time
		self.quality = quality
		self.angle = angle
		self.distance = distance
	
	def __str__(self):
		return "Id: {0} T: {1} Q: {2} A: {3} D: {4}".format(
		self.scan_id, self.date_time, self.quality,
		self.angle, self.distance)
