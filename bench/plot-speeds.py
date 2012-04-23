"""Script for plotting the results of the 'suite' benchmark.
Invoke without parameters for usage hints.

:Author: Francesc Alted
:Date: 2010-06-01
"""

import matplotlib as mpl
from pylab import *

KB_ = 1024
MB_ = 1024*KB_
GB_ = 1024*MB_
NCHUNKS = 128    # keep in sync with bench.c

linewidth=2
#markers= ['+', ',', 'o', '.', 's', 'v', 'x', '>', '<', '^']
#markers= [ 'x', '+', 'o', 's', 'v', '^', '>', '<', ]
markers= [ 's', 'o', 'v', '^', '+', 'x', '>', '<', '.', ',' ]
markersize = 8

def get_values(filename):
    f = open(filename)
    values = {"memcpyw": [], "memcpyr": []}

    for line in f:
        if line.startswith('-->'):
            tmp = line.split('-->')[1]
            nthreads, size, elsize, sbits = [int(i) for i in tmp.split(', ')]
            values["size"] = size * NCHUNKS / MB_;
            values["elsize"] = elsize;
            values["sbits"] = sbits;
            # New run for nthreads
            (ratios, speedsw, speedsr) = ([], [], [])
            # Add a new entry for (ratios, speedw, speedr)
            values[nthreads] = (ratios, speedsw, speedsr)
            #print "-->", nthreads, size, elsize, sbits
        elif line.startswith('memcpy(write):'):
            tmp = line.split(',')[1]
            memcpyw = float(tmp.split(' ')[1])
            values["memcpyw"].append(memcpyw)
        elif line.startswith('memcpy(read):'):
            tmp = line.split(',')[1]
            memcpyr = float(tmp.split(' ')[1])
            values["memcpyr"].append(memcpyr)
        elif line.startswith('comp(write):'):
            tmp = line.split(',')[1]
            speedw = float(tmp.split(' ')[1])
            ratio = float(line.split(':')[-1])
            speedsw.append(speedw)
            ratios.append(ratio)
        elif line.startswith('decomp(read):'):
            tmp = line.split(',')[1]
            speedr = float(tmp.split(' ')[1])
            speedsr.append(speedr)
            if "OK" not in line:
                print "WARNING!  OK not found in decomp line!"

    f.close()
    return nthreads, values


def show_plot(plots, yaxis, legends, gtitle):
    xlabel('Compresssion ratio')
    ylabel('Speed (MB/s)')
    title(gtitle)
    xlim(0, None)
    #ylim(0, 10000)
    ylim(0, None)
    grid(True)

#     legends = [f[f.find('-'):f.index('.out')] for f in filenames]
#     legends = [l.replace('-', ' ') for l in legends]
    #legend([p[0] for p in plots], legends, loc = "upper left")
    legend([p[0] for p in plots
            if not isinstance(p, mpl.lines.Line2D)],
           legends, loc = "best")


    #subplots_adjust(bottom=0.2, top=None, wspace=0.2, hspace=0.2)
    if outfile:
        print "Saving plot to:", outfile
        savefig(outfile)
    else:
        show()

if __name__ == '__main__':

    from optparse import OptionParser

    usage = "usage: %prog [-o outfile] [-t title ] [-d|-c] filename"
    compress_title = 'Compression speed'
    decompress_title = 'Decompression speed'
    yaxis = 'No axis name'

    parser = OptionParser(usage=usage)
    parser.add_option('-o',
                      '--outfile',
                      dest='outfile',
                      help='filename for output')

    parser.add_option('-t',
                      '--title',
                      dest='title',
                      help='title of the plot',)

    parser.add_option('-d', '--decompress', action='store_true',
            dest='dspeed',
            help='plot decompression data',
            default=False)
    parser.add_option('-c', '--compress', action='store_true',
            dest='cspeed',
            help='plot compression data',
            default=False)

    (options, args) = parser.parse_args()
    if len(args) == 0:
        parser.error("No input arguments")
    elif len(args) > 1:
        parser.error("Too many input arguments")
    else:
        pass

    if options.dspeed and options.cspeed:
        parser.error("Can only select one of [-d, -c]")
    elif options.cspeed:
        options.dspeed = False
        plot_title = compress_title
    else: # either neither or dspeed
        options.dspeed = True
        plot_title = decompress_title

    filename = args[0]
    outfile = options.outfile
    cspeed = options.cspeed
    dspeed = options.dspeed

    plots = []
    legends = []
    nthreads, values = get_values(filename)
    #print "Values:", values

    if options.title:
        plot_title = options.title
    else:
        plot_title += " (%(size).1f MB, %(elsize)d bytes, %(sbits)d bits)" % values

    gtitle = plot_title

    for nt in range(1, nthreads+1):
        #print "Values for %s threads --> %s" % (nt, values[nt])
        (ratios, speedw, speedr) = values[nt]
        if cspeed:
            speed = speedw
        else:
            speed = speedr
        #plot_ = semilogx(ratios, speed, linewidth=2)
        plot_ = plot(ratios, speed, linewidth=2)
        plots.append(plot_)
        nmarker = nt
        if nt >= len(markers):
            nmarker = nt%len(markers)
        setp(plot_, marker=markers[nmarker], markersize=markersize,
             linewidth=linewidth)
        legends.append("%d threads" % nt)

    # Add memcpy lines
    if cspeed:
        mean = sum(values["memcpyw"]) / nthreads
        message = "memcpy (write to memory)"
    else:
        mean = sum(values["memcpyr"]) / nthreads
        message = "memcpy (read from memory)"
    plot_ = axhline(mean, linewidth=3, linestyle='-.', color='black')
    text(4.0, mean+50, message)
    plots.append(plot_)
    show_plot(plots, yaxis, legends, gtitle)


