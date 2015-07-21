#!/usr/bin/env python
"""convert a Segy object to a kml representation for Google Earth/Oceans et al."""

import sys
import simplesegy.segy as segy

def metadata_placemark(out,metadata,filename,extra_html='',indent='    '):
    out.write(indent+'<Placemark>\n')
    out.write(indent+'  <name>%s</name>\n' % filename)
    out.write(indent+'  <description><![CDATA[\n')
    out.write(indent+'      %s\n' % str(metadata))
    out.write(extra_html)
    out.write(indent+'    ]]>\n')
    out.write(indent+'  </description>\n')
    out.write(indent+'  <Point>\n')
    x1 = metadata[0]
    x2 = metadata[1]
    midpoint = (x1[0] + (x2[0]-x1[0])/2.,x1[1] + (x2[1]-x1[1])/2.)
    out.write(indent+'    <coordinates>%f,%f,0</coordinates>\n' % midpoint)
    out.write(indent+'  </Point>\n')

    out.write(indent+'</Placemark>\n')

def bbox(out,metadata,name,indent='    '):
    bounds = {
        'xmin':metadata[0][0],
        'ymin':metadata[0][1],
        'xmax':metadata[1][0],
        'ymax':metadata[1][1]
        }

    #sys.stderr.write(str(bounds)+'\n')
    out.write(indent+'<Placemark>\n')
    out.write(indent+'  <name>bbox for %s</name>\n' % name)
    out.write(indent+'  <description><![CDATA[\n')
    out.write(indent+'      %s\n' % str(metadata))
    out.write(indent+'    ]]>\n')
    out.write(indent+'  </description>\n')
    out.write('''
<Polygon>
			<tessellate>1</tessellate>
			<outerBoundaryIs>
				<LinearRing>
					<coordinates>
{xmin},{ymin},0 {xmin},{ymax},0 {xmax},{ymax},0 {xmax},{ymin},0 {xmin},{ymin},0 </coordinates>
				</LinearRing>
			</outerBoundaryIs>
		</Polygon>'''.format(**bounds))
    out.write(indent+'</Placemark>\n')

def addStyle(out,lineColor='a0a0a0',polyColor="808080",polyOpacity=.25,lineOpacity=.5,lineWidth=5,indent='    ',styleName='style'):
    '''
    @param polyOpacity: 0..1 where 1 is opaque, and 0 is not visible
    '''
    o=out
    lo = (int(lineOpacity*255)).__hex__()
    lo = lo[lo.find('x')+1:]
    if len(lo)==1: lo='0'+lo
    po = (int(polyOpacity*255)).__hex__()
    po = po[po.find('x')+1:]
    if len(po)==1: po='0'+po
    
    o.write(indent+'<Style id="'+styleName+'">\n')
    o.write(indent+'\t<LineStyle>'+'\n')
    o.write(indent+'\t  <color>'+lo+str(lineColor)+'</color>\n')
    o.write(indent+'\t  <width>'+str(lineWidth)+'</width>\n')
    o.write(indent+'\t</LineStyle>'+'\n')
    o.write(indent+'\t<PolyStyle>'+'\n')
    o.write(indent+'\t  <color>'+po+str(polyColor)+'</color>\n')
    o.write(indent+'\t</PolyStyle>'+'\n')
    o.write(indent+'</Style>'+'\n')


def track_line(out,sgy,name,indent='    '):
    last=None
    try:
        for trace in sgy:
            if not last:
                last = trace
                continue
            x1,y1 = last.position_geographic()
            x2,y2 = trace.position_geographic()

            out.write('<Placemark>\n')
        #if options.withStyle: print '<styleUrl>#'+options.styleName+'</styleUrl>'

#            out.write('<LineString><coordinates>'+str(start[0])+','+str(start[1])+',10 '+str(end[0])+','+str(end[1])+',10</coordinates></LineString>\n')
            #sys.stderr.write('%f, %f, %f, %f\n' % (x1,y1,x2,y2))
            out.write('<LineString><coordinates>%.5f,%.5f,10 %.5f,%.5f,10</coordinates></LineString>\n' % (x1,y1,x2,y2))


        #out.write('<TimeSpan><begin>'+timeSec2KmlTime(_t)+'</begin><end>'+timeSec2KmlTime(t)+'</end></TimeSpan>'
            out.write('</Placemark>\n')
            last = trace
    except segy.SegyTraceError,e:
        sys.stderr.write('    Exception: %s\n' %  str(e))

def convert(out, sgy, 
            summary=False,
            text_header=False,
            bin_header=False, 
            all_traces=False,
            trace_fields=None,
            trace_num=None,
            verbose=False):

    metadata = sgy.trace_metadata()

    out.write('''<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2">
  <Folder>
''')
    metadata_placemark(out,metadata,sgy.filename)
    bbox(out,metadata,sgy.filename)
    track_line(out,sgy,sgy.filename)
    out.write('''  </Folder>
</kml>
''')
