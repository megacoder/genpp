#!/usr/bin/env python
# vim: noet sw=4 ts=4

import	datetime
import	os
import	sys

class	OswTicker( object ):

	def	__init__( self, fmt = '%a %b %d %H:%M:%S %Y' ):
		self.fmt       = fmt
		self.old_delta = None
		self.last      = None
		self.stats     = dict(
			good  = 0,
			early = 0,
			late  = 0
		)
		return

	def	tick( self, tick ):
		dt = datetime.datetime.strptime(
			tick,
			self.fmt
		)
		if self.last is None:
			self.last = dt
			delta     = datetime.timedelta()
			mark      = ' '
			self.stats['good'] += 1
		else:
			delta = dt - self.last
			if self.old_delta is None:
				mark = ' '
				self.old_delta = delta
				self.stats['good'] += 1
			else:
				if delta < self.old_delta:
					self.stats['early'] += 1
					mark = '-'
				elif delta > self.old_delta:
					mark = '+'
					self.stats['late'] += 1
				else:
					mark = ' '
					self.stats['good'] += 1
		self.last      = dt
		self.old_delta = delta
		s = '{0} {1} {2}'.format(
			mark,
			tick,
			delta
		)
		return s

	def	report( self, out = sys.stdout ):
		if out:
			header = 'Jitter Statistics'
			self.println( '', file = out )
			self.println(
				'{0}'.format( header ),
				file = out
			)
			self.println(
				'{0}'.format( '-' * len(header) ),
				file = out
			)
			fmt = '{0:5} {1}'
			self.println(
				fmt.format(
					'Good',
					self.stats['good']
				),
				file = out
			)
			self.println(
				fmt.format(
					'Early',
					self.stats['early']
				),
				file = out
			)
			self.println(
				fmt.format(
					'Late',
					self.stats['late']
				),
				file = out
			)
		return
