#!/usr/bin/python
# vim: noet sw=4 ts=4

import	sys
import	os
import	subprocess
import	hashlib
import	argparse

try:
	from	PIL		import	Image
except Exception, e:
	print >>sys.stderr, 'No imaging library?'
	exit( 1 )

class	Deduplicate( object ):

	def	__init__( self ):
		self.name_to_hash = dict()
		self.hash_to_names = dict()
		self.ignored      = dict()
		self.ignored      = [ '.git' ]
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
			except:
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
			# Hack: make sure thumbnail is listed twice so it will be
			# discarded.
			self.hash_to_names[ hash ] += [ name ]
		if name not in self.name_to_hash:
			self.name_to_hash[ name ] = hash
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
			metavar = 'SCRIPT',
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
		return

	def	report( self ):
		total    = 0
		deleted  = 0
		original = 0
		# Sort by hash owner filenames
		for name in sorted( self.name_to_hash ):
			original += 1
			hash = self.name_to_hash[ name ]
			print '# {0}  {1}'.format(
				hash,
				name,
			)
			collisions = self.hash_to_names[ hash ][1:]
			total += len( collisions )
			for goner in sorted( collisions ):
				deleted += 1
				print '$ rm -f {0}'.format( goner )
				if not self.args.kidding:
					try:
						os.unlink( name )
					except Exception, e:
						pass
		fmt = '# {0:6d} {1}'
		print fmt.format( original, 'original' )
		print fmt.format( deleted, 'deleted' )
		print fmt.format( total,   'total' )
		return

if __name__ == '__main__':
	exit( Deduplicate().main() )
