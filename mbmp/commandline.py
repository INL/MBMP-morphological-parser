## Python implementation of MBMA (Van den Bosch & Daelemans 1999)

## Copyright (C) 2011 Institute for Dutch Lexicology (INL)
## Author: Folgert Karsdorp, INL
## E-mail: <servicedesk@inl.nl>
## URL: <http://www.inl.nl/>
## For licence information, see LICENCE.TXT

"""
Commandline interface to mbmp.
"""

import argparse
import codecs
import os
import sys
import time

import mbmp.config as config
from mbmp.classifiers import MBMA, MBMS, MBMC, MBLEM, MBPT
from mbmp.parse import MbmaParser, MbmaCKYParser


def demo(draw_parses=None, print_parses=None):
    """
    A simple demo showing some basic functionality.
    """
    demos = ['aandeelhoudersvergadering', 'hardloopwedstrijd']
    trees = []
    with MBMA() as program:
        for word in demos:
            print 'Parsing: %s' % word
            results = program.classify(word)
            trees.extend(program.trees(results))
    if draw_parses is None:
        print
        print 'Draw parses (y/n)?',
        draw_parses = sys.stdin.readline().strip().lower().startswith('y')
    if draw_parses:
        from nltk.draw.tree import draw_trees
        print '  please wait...'
        draw_trees(*trees)

    if print_parses is None:
        print
        print 'Print parses (y/n)?',
        print_parses = sys.stdin.readline().strip().lower().startswith('y')
    if print_parses:
        for parse in trees:
            print parse

class CommandLine(argparse.ArgumentParser):
    """Commandline options for mbmp."""
    def __init__(self):
        argparse.ArgumentParser.__init__(self, prog = 'mbmp', description = '''
            Memory-Based Morphological Parsing (MBMP), an implementation of
            MBMA with extended functionality in Python based on
            Van den Bosch & Daelemans (1999).

            For more options, see the config.py file.''')
            
        self.add_argument(
            '-f', dest = 'trainingfile', type = str, required = False,
            help = 'the path pointing to the trainingfile.')
        self.add_argument(
            '-i', dest = 'instancebase', type = str, required = False,
            help = 'the path pointing to the instance-base.')
        self.add_argument(
            '-t', dest = 'testfile', type = str,
            required = True, help = '''The path pointing to the testfile.
            File must consist of one word per line''')
        self.add_argument(
            '-o', dest = 'output', type = argparse.FileType('w'),
            required = False, default = sys.stdout,
            help = 'the path pointing to the output file.')
        self.add_argument(
            '-p', dest = 'process', type = str, required = False,
            default='parse',
            choices = [
                'parse', 'segmentize', 'lemmatize', 'pos-tagging', 'chunk'],
            help = 'Choose what classification to perform.')
        self.add_argument(
            '--parser', dest = 'parser', type=str, required = False,
            default = 'pcfg', choices = ['cfg', 'pcfg'],
            help = 'Choose what parser to use.')
        self.add_argument(
            '--lemmatize', dest = 'morph_repr', type = str, required = False,
            default = 'token',
            choices = ['tokens', 'lemmas', 'tokens-and-lemmas'],
            help = '''Choose how te represent the morphemes in the printed
            trees. "lemmas" returns a lemmatized representation of the
            morphemes, "tokens" returns the original segmentation of the
            morphemes and "tokens-and-lemmas" returns a representation like
            token=lemma.''')
        self.add_argument(
            '--pprint', dest = 'print_tree', action = 'store_const',
            const=True, default = False,
            help = '''Return a (pretty) hierarchical tree  representation of
            the parse (only works with option 'parse' and 'chunk').''')
        self.add_argument(
            '--port', dest = "port", type = int, required = False,
            default = False, help = 'The tcp port for timblserver')
        self.add_argument(
            '--version', action='version', version='%(prog)s 0.3')
            
            
def main():
    args = CommandLine().parse_args()

    # setup the chosen classifier and load the appropriate configuration
    if args.process == 'parse':
        classifier, settings = MBMA, config.MBMA_CONFIG
    elif args.process == 'chunk':
        classifier, settings = MBMC, config.MBMC_CONFIG
    elif args.process == 'segmentize':
        classifier, settings = MBMS, config.MBMS_CONFIG
    elif args.process == 'lemmatize':
        classifier, settings = MBLEM, config.MBLEM_CONFIG
    elif args.process == 'pos-tagging':
        classifier, settings = MBPT, config.MBPT_CONFIG

    # if another PORT is chosen, set it in CONFIG
    if args.port:
        config.PORT = args.port
        
    # check if trainingfile or instancebase is an existing file and
    # add this to the configuration. If no file is given we stick
    # to the default file with that comes with a particular classifier
    if args.trainingfile:
        if not os.path.isfile(args.trainingfile):
            raise IOError('Trainingfile not found')
        settings['f'] = args.trainingfile
        del settings['i']
    elif args.instancebase:
        if not os.path.isfile(args.instancebase):
            raise IOError('Instancebase not found')
        settings['i'] = args.instancebase

    # if hierarchical parsing is chosen, initialize the parser
    if args.process == 'parse' and args.print_tree:
        if args.parser == 'cfg':
            parser = MbmaParser
        else:
            sys.stderr.write('Loading PCFG...\n')
            parser = MbmaCKYParser
    else:
        parser = None
    # initialize the classifier (best to do this in a with-statement
    # so that in case of any unexpected errors, the timbl server is killed.)
    with classifier(config.HOST, config.PORT,
                    settings, parser=parser) as program:
        counter = 0
        count_limit = 100
        args.output.write(codecs.BOM_UTF8)
        # process all words each at a time
        for i, word in enumerate(codecs.open(args.testfile,
                                             encoding=config.ENCODING)):
            counter += 1
            word = word.strip()
            if ' ' in word:
                sys.stderr.write(
                    'No spaces allowed within words! skipping %r\n' % word)
                continue
            results = program.classify(word)
            if args.print_tree and args.process in ('parse', 'chunk'):
                if args.process == 'parse':
                    args.output.write(
                        u'# {0} {1}:\n'.format(i, word).encode('utf-8'))
                    trees = list(program.trees(results, mrepr=args.morph_repr))
                    if not trees:
                        args.output.write(
                            u'   {0} {1}\n'.format(
                                1, program.pprint_parse(results)).encode('utf-8'))
                    else:
                        for j, tree in enumerate(trees):
                            args.output.write(
                                u'   {0} {1}\n'.format(
                                    j+1, tree.pprint(indent=5)).encode('utf-8'))
                else:
                    args.output.write(
                        u'# {0} {1}:\n'.format(i, word).encode('utf-8'))
                    trees = program.trees(results)
                    args.output.write(
                        u'# {0}\n'.format(
                            trees.pprint(indent=2)).encode('utf-8'))
            elif args.process == 'pos-tagging':
                args.output.write(
                    u'{0}\t{1}\n'.format(word, results).encode('utf-8'))
            else:
                args.output.write(
                    u'# {0} {1}\t{2}\n'.format(
                        i, word, program.pprint_parse(results)).encode('utf-8'))
            if counter == count_limit:
                sys.stderr.write(
                    'Processed: {0} words @ {1}\n'.format(
                        counter, time.ctime()))
                count_limit *= 2

if __name__ == '__main__':
    main()
