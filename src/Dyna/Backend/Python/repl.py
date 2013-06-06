import os, sys
import cmd, readline
from utils import blue, yellow, green, magenta, ip

from interpreter import AggregatorConflict
import debug

class REPL(cmd.Cmd, object):

    def __init__(self, interp, hist):
        self.interp = interp
        cmd.Cmd.__init__(self)
        self.hist = hist
        if not os.path.exists(hist):
            readline.clear_history()
            with file(hist, 'wb') as f:
                f.write('')
        readline.read_history_file(hist)
        self.do_trace('off')
        self.lineno = 0

    @property
    def prompt(self):
        return ':- ' #% self.lineno

    def do_exit(self, _):
        readline.write_history_file(self.hist)
        return -1

    def do_EOF(self, args):
        "Exit on end of file character ^D."
        print 'exit'
        return self.do_exit(args)

    def precmd(self, line):
        """
        This method is called after the line has been input but before it has
        been interpreted. If you want to modify the input line before execution
        (for example, variable substitution) do it here.
        """
        return line

    def postcmd(self, stop,  line):
        self.lineno += 1
        return stop

    def do_chart(self, _):
#        if not args:
        self.interp.dump_charts()
#        else:
#            unrecognized = set(args.split()) - set(interp.chart.keys())
#            for f in unrecognized:
#                print 'unrecognized predicate', f
#            if unrecognized:
#                print 'available:\n\t' + '\t'.join(chart.keys())
#                return
#            for f in args.split():
#                print chart[f]
#                print
#            interp.dump_errors()

    def emptyline(self):
        """Do nothing on empty input line"""
        pass

    def do_ip(self, _):
        ip()

    def do_trace(self, args):
        if args == 'on':
            self.interp.trace = sys.stdout
        elif args == 'off':
            self.interp.trace = file(os.devnull, 'w')
        else:
            print 'Did not understand argument %r please use (on or off).' % args

#    def do_debug(self, line):
#        dynac_code(line, debug=True, run=False)

    def do_query(self, line):

        if line.endswith('.'):
            print "Queries don't end with a dot."
            return

        query = 'out(%s) dict= _VALUE is (%s), _VALUE.' % (self.lineno, line)

        print blue % query

        self.default(query)

        for (_, results) in self.interp.chart['out/1'][self.lineno,:]:
            for result in results:
                print result
        print

    def default(self, line):
        """
        Called on an input line when the command prefix is not recognized.  In
        that case we execute the line as Python code.
        """
        line = line.strip()
        if not line.endswith('.'):
            print "ERROR: Line doesn't end with period."
            return
        try:
            src = self.interp.dynac_code(line)  # failure.

            changed = self.interp.do(src)

        except AggregatorConflict as e:
            print 'AggregatorConflict:', e

        else:
            if not changed:
                return
            print '============='
            for x, v in sorted(changed.items()):
                print '%s := %r' % (x, v)
            print
            self.interp.dump_errors()

    def do_draw(self, _):
        self.interp.draw()

    def cmdloop(self, _=None):
        try:
            super(REPL, self).cmdloop()
        except KeyboardInterrupt:
            print '^C'
            self.cmdloop()
        except Exception as e:
            readline.write_history_file(self.hist)
            raise e
