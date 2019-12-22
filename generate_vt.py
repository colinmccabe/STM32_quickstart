# I am *so. done.* writing vector tables by hand. Help me out, Python?
import sys

if not len( sys.argv ) == 3:
  sys.exit( 1 )

irq_lines = []
irq_appending = 0
vt_fn = sys.argv[ 1 ] + '_vt.S'
dev_hdr_fp = 'device_headers/' + sys.argv[1].lower() + '.h'

with open( dev_hdr_fp, 'r' ) as dev_hdr:
  for line in dev_hdr:
    if irq_appending == 1:
      irq_lines.append( line )
      if 'IRQn_Type' in line:
        irq_appending = 2
    elif irq_appending == 0:
      if 'Interrupt Number Definition' in line:
        irq_appending = 1

irq_dict = { }
for line in irq_lines:
  if '=' in line:
    while '  ' in line:
      line = line.replace( '  ', ' ' )
    line = line.replace( ',', '' )
    blocks = line.split( ' ' )
    irq_dict[ int( blocks[ 3 ] ) ] = blocks[ 1 ]

irq_list = sorted( irq_dict.items() )

with open( vt_fn, 'w+' ) as vt_as:
  vt_as.write( '/* Autogenerated vector table for ' +
               sys.argv[ 1 ] + ' */\n\n' )
  vt_as.write( '.syntax unified\n' )
  vt_as.write( '.cpu ' + sys.argv[ 2 ] + '\n' )
  vt_as.write( '.thumb\n\n' )
  vt_as.write( '.global vtable\n' )
  vt_as.write( '.global default_interrupt_handler\n\n' )
  vt_as.write( '.type vtable, %object\n' )
  vt_as.write( '.section .vector_table,"a",%progbits\n' )
  vt_as.write( 'vtable:\n' )
  vt_as.write( '  .word _estack\n' )
  vt_as.write( '  .word reset_handler\n' )
  for i in range( irq_list[ 0 ][ 0 ], ( irq_list[ -1 ][ 0 ] + 1 ) ):
    if i in irq_dict:
      vt_as.write( '  .word ' + irq_dict[ i ] + '_handler\n' )
    else:
      vt_as.write( '  .word 0\n' )
  vt_as.write( '\n' )
  for i in range( irq_list[ 0 ][ 0 ], ( irq_list[ -1 ][ 0 ] + 1 ) ):
    if i in irq_dict:
      vt_as.write( '  .weak ' + irq_dict[ i ] + '_handler\n' )
      vt_as.write( '  .thumb_set ' + irq_dict[ i ] + '_handler,default_interrupt_handler\n' )
  vt_as.write( '.size vtable, .-vtable\n\n' )
  vt_as.write( '.section .text.default_interrupt_handler,"ax",%progbits\n' )
  vt_as.write( 'default_interrupt_handler:\n' )
  vt_as.write( '  default_interrupt_loop:\n' )
  vt_as.write( '    B default_interrupt_loop\n' )
  vt_as.write( '.size default_interrupt_handler, .-default_interrupt_handler\n' )

sys.exit( 0 )
