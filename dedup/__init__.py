#!/usr/bin/python
# vim: noet sw=4 ts=4

import	sys
import	os
import	subprocess
import	hashlib
import	argparse

try:
	from	version	import	Version
except:
	Version = 'What Tommy Found'

try:
	from	PIL		import	Image
except Exception, e:
	print >>sys.stderr, 'No imaging library?'
	exit( 1 )

class	Deduplicate( object ):

	def	__init__( self, out = sys.stdout ):
		self.hash_to_names = dict()
		self.ignored       = dict()
		self.out           = out
		self.ignored	   = dict({
			'.git' : 0,
		})
		return

	def	chatter( self, s ):
		print >>self.out, s
		return

	def	_do_name( self, name ):
		#
		too_small = False
		if self.min_area:
			try:
				image                    = Image.open( name )
				(xmin, ymin, xmax, ymax) = image.getbbox()
				width                    = xmax - xmin
				height                   = ymax - ymin
				area                     = width * height
				if area < self.min_area:
					too_small = True
					if self.args.verbose:
						self.chatter(
							'bbox( {0}, {1}, {2}, {3} ) too small: {4}'.format(
								xmin, ymin,
								xmax, ymax,
								name
							)
						)
			except Exception, e:
				if self.args.verbose:
					self.chatter(
						'not an image: {0} [{1}]'.format( name, e )
					)
				pass
		#
		h = hashlib.md5()
		if self.args.verbose:
			self.chatter(
				'Calculating checksum for {0}'.format( name )
			)
		with open( name ) as f:
			h.update( f.read() )
		hash = h.hexdigest()
		self.hash_to_names[ hash ] = self.hash_to_names.get( hash, list() ) + [ name ]
		if too_small:
			# Hack: make sure thumbnail is listed twice so all thumbnails will
			# be discarded.
			self.hash_to_names[ hash ] += [ name ]
		# print '{0}\t{1}'.format( hash, name )
		return

	def	process( self, name = '.' ):
		if os.path.isdir( name ):
			if self.args.verbose:
				self.chatter(
					'Processing directory: {0}'.format( name )
				)
			for rootdir, dirs, names in os.walk( name ):
				for i, entry in enumerate(dirs):
					if entry in self.ignored:
						del dirs[i]
				for name in names:
					fn = os.path.join( rootdir, name )
					self._do_name( fn )
		elif os.path.isfile( name ):
			if self.args.verbose:
				self.chatter(
					'Processing file: {0}'.format( name )
				)
			self._do_name( name )
		else:
			if self.args.verbose:
				self.chatter(
					'Ignoring name {0}'.format( name )
				)
			pass
		return

	def	main( self ):
		p = argparse.ArgumentParser(
			description = ''' Delete files with duplicate checksums. '''
		)
		p.add_argument(
			'-g',
			'--geom',
			dest    = 'geom',
			metavar = 'NxM',
			default = None,
			help    = 'smaller than this is a thumbnail',
		)
		p.add_argument(
			'-n',
			'--kidding',
			dest   = 'kidding',
			action = 'store_true',
			help   = 'show what would be done',
		)
		p.add_argument(
			'-o',
			'--out',
			dest    = 'out',
			default = None,
			metavar = 'FILE',
			help    = 'write commands here inst4ead of stdout',
		)
		p.add_argument(
			'-v',
			'--verbose',
			dest   = 'verbose',
			action = 'store_true',
			help   = 'chatter about our activities',
		)
		p.add_argument(
			'--version',
			action  = 'version',
			version = Version,
			help    = 'Program Version {0}'.format( Version ),
		)
		p.add_argument(
			dest    = 'names',
			metavar = 'FILE',
			nargs   = '*',
			default = [ '.' ],
			help    = 'directory or file to process'
		)
		self.args = p.parse_args()
		if self.args.geom:
			parts = map(
				lambda s : int( s.strip() ),
				self.args.geom.split( 'x', 1 )
			)
			self.min_area = 1
			for i in range( len( parts ) ):
				self.min_area *= parts[i]
		else:
			self.min_area = None
		if self.args.out:
			sys.stdout = open( self.args.out, 'w' )
		for name in self.args.names:
			self.process( name )
		self.report()
		return 0

	def	report( self ):
		# For each hash, keep only the shortest filename and
		# delete all others.
		for hash in self.hash_to_names:
			names = self.hash_to_names[ hash ]
			if len( names ) > 1:
				# Collisions on this hash, delete extras
				names.sort(
					key = lambda s : len( s )
				)
				print '# {0}  {1}'.format(
					hash,
					names[0]
				)
				for goner in names[1:]:
					if self.args.kidding:
						print "rm -f '{0}'".format( goner )
					else:
						if self.args.verbose:
							print "rm -f '{0}'".format( goner )
						try:
							os.unlink( goner )
						except Exception, e:
							pass
		return

if __name__ == '__main__':
	exit( Deduplicate().main() )
