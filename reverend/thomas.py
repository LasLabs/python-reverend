# This module is part of the Divmod project and is Copyright 2003 Amir Bakhtiar:
# amir@divmod.org.  This is free software; you can redistribute it and/or
# modify it under the terms of version 2.1 of the GNU Lesser General Public
# License as published by the Free Software Foundation.
#

import math
import operator
import pickle
import re

try:
    set
except NameError:
    # Fall back to the sets module if there's no set builtin yet.
    from sets import Set as set


class BayesData(dict):

    def __init__(self, name='', pool=None):
        self.name = name
        self.training = []
        self.pool = pool
        self.tokenCount = 0
        self.trainCount = 0

    def trained_on(self, item):
        return item in self.training

    def __repr__(self):
        return '<BayesDict: %s, %s tokens>' % (self.name, self.tokenCount)


class Bayes(object):

    def __init__(self, tokenizer=None, combiner=None, data_class=None):
        if data_class is None:
            self.DataClass = BayesData
        else:
            self.DataClass = data_class
        self.corpus = self.DataClass('__Corpus__')
        self.pools = {
            '__Corpus__': self.corpus,
        }
        self.trainCount = 0
        self.dirty = True
        # The tokenizer takes an object and returns
        # a list of strings
        if tokenizer is None:
            self._tokenizer = Tokenizer()
        else:
            self._tokenizer = tokenizer
        # The combiner combines probabilities
        if combiner is None:
            self.combiner = self.robinson
        else:
            self.combiner = combiner

    def commit(self):
        self.save()

    def new_pool(self, pool_name):
        """Create a new pool, without actually doing any training."""
        self.dirty = True # not always true, but it's simple
        return self.pools.setdefault(pool_name, self.DataClass(pool_name))

    def remove_pool(self, pool_name):
        del self.pools[pool_name]
        self.dirty = True

    def rename_pool(self, pool_name, new_name):
        self.pools[new_name] = self.pools[pool_name]
        self.pools[new_name].name = new_name
        self.remove_pool(pool_name)
        self.dirty = True

    def merge_pools(self, dest_pool, source_pool):
        """Merge an existing pool into another.

        The data from source_pool is merged into dest_pool.
        The arguments are the names of the pools to be merged.
        The pool named source_pool is left in tact and you may
        want to call remove_pool() to get rid of it.
        """
        sp = self.pools[source_pool]
        dp = self.pools[dest_pool]
        for tok, count in sp.items():
            if dp.get(tok):
                dp[tok] += count
            else:
                dp[tok] = count
                dp.tokenCount += 1
        self.dirty = True

    def pool_data(self, pool_name):
        """Return a list of the (token, count) tuples."""
        return self.pools[pool_name].items()

    def pool_tokens(self, pool_name):
        """Return a list of the tokens in this pool."""
        return [tok for tok, count in self.pool_data(pool_name)]

    def save(self, file_path='bayesdata.dat'):
        """Save the trained model to the appropriate path.

        Args:
            file_path (str): Path of database file.
        """
        with open(file_path, 'wb') as fp:
            self.save_pointer(fp)

    def save_handler(self, file_handler):
        """Save the trained model to the open file handler.

        Args:
            file_handler (file): Open file pointer, or file-like object.
        """
        pickle.dump(self.pools, file_handler)

    def load(self, file_path='bayesdata.dat'):
        """Load trained model data from a file path.

        Args:
            file_path (str): Path of database file.
        """
        with open(file_path, 'rb') as fp:
            self.load_handler(fp)

    def load_handler(self, file_handler):
        """Load trained model data from an open file handler.

        Args:
            file_handler (file): Open file pointer, or file-like object.
        """
        self.pools = pickle.load(file_handler)
        self.corpus = self.pools['__Corpus__']
        self.dirty = True

    def pool_names(self):
        """Return a sorted list of Pool names.

        Does not include the system pool '__Corpus__'.
        """
        pools = self.pools.keys()
        pools.remove('__Corpus__')
        pools = [pool for pool in pools]
        pools.sort()
        return pools

    def build_cache(self):
        """Merges corpora and computes probabilities."""
        self.cache = {}
        for pname, pool in self.pools.items():
            # skip our special pool
            if pname == '__Corpus__':
                continue

            poolCount = pool.tokenCount
            themCount = max(self.corpus.tokenCount - poolCount, 1)
            cacheDict = self.cache.setdefault(pname, self.DataClass(pname))

            for word, totCount in self.corpus.items():
                # for every word in the copus
                # check to see if this pool contains this word
                thisCount = float(pool.get(word, 0.0))
                if (thisCount == 0.0):
                        continue
                otherCount = float(totCount) - thisCount

                if not poolCount:
                    goodMetric = 1.0
                else:
                    goodMetric = min(1.0, otherCount/poolCount)
                badMetric = min(1.0, thisCount/themCount)
                f = badMetric / (goodMetric + badMetric)

                # PROBABILITY_THRESHOLD
                if abs(f-0.5) >= 0.1 :
                    # GOOD_PROB, BAD_PROB
                    cacheDict[word] = max(0.0001, min(0.9999, f))

    def pool_probs(self):
        if self.dirty:
            self.build_cache()
            self.dirty = False
        return self.cache

    def get_tokens(self, obj):
        """By default, we expect obj to be a screen and split on whitespace.

        Note that this does not change the case.
        In some applications you may want to lowecase everthing
        so that "king" and "King" generate the same token.

        Override this in your subclass for objects other
        than text.

        Alternatively, you can pass in a tokenizer as part of
        instance creation.
        """
        return self._tokenizer.tokenize(obj)

    def get_probs(self, pool, words):
        """Extracts the probabilities of tokens in a message."""
        probs = [(word, pool[word]) for word in words if word in pool]
        probs.sort(lambda x,y: cmp(y[1],x[1]))
        return probs[:2048]

    def train(self, pool, item, uid=None):
        """Train Bayes by telling him that item belongs in pool.

        ``uid`` is optional and may be used to uniquely identify the
        item that is being trained on.
        """
        tokens = self.get_tokens(item)
        pool = self.pools.setdefault(pool, self.DataClass(pool))
        self._train(pool, tokens)
        self.corpus.trainCount += 1
        pool.trainCount += 1
        if uid:
            pool.training.append(uid)
        self.dirty = True

    def untrain(self, pool, item, uid=None):
        tokens = self.get_tokens(item)
        pool = self.pools.get(pool, None)
        if not pool:
            return
        self._untrain(pool, tokens)
        # I guess we want to count this as additional training?
        self.corpus.trainCount += 1
        pool.trainCount += 1
        if uid:
            pool.training.remove(uid)
        self.dirty = True

    def _train(self, pool, tokens):
        wc = 0
        for token in tokens:
            count = pool.get(token, 0)
            pool[token] =  count + 1
            count = self.corpus.get(token, 0)
            self.corpus[token] =  count + 1
            wc += 1
        pool.tokenCount += wc
        self.corpus.tokenCount += wc

    def _untrain(self, pool, tokens):
        for token in tokens:
            count = pool.get(token, 0)
            if count:
                if count == 1:
                    del(pool[token])
                else:
                    pool[token] =  count - 1
                pool.tokenCount -= 1

            count = self.corpus.get(token, 0)
            if count:
                if count == 1:
                    del(self.corpus[token])
                else:
                    self.corpus[token] =  count - 1
                self.corpus.tokenCount -= 1

    def trained_on(self, msg):
        for p in self.cache.values():
            if msg in p.training:
                return True
        return False

    def guess(self, message):
        """Guess which buckets the message belongs to.

        Args:
            message (str): The message string to tokenize and subsequently
            classify.

        Returns:
            list of tuple: List of tuple pairs indicating which bucket(s) the
            message string is guessed to be classified under, and the ratio of
            certainty for this guess. As an example, a 99% probability that
            the input is a ``fowl`` would look like ``[('fowl', 0.9999)]``.
        """

        tokens = set(self.get_tokens(message))
        pools = self.pool_probs()

        res = {}
        for pool_name, pool_probs in pools.items():
            p = self.get_probs(pool_probs, tokens)
            if len(p):
                res[pool_name] = self.combiner(p, pool_name)

        res = res.items()
        res.sort(lambda x, y: cmp(y[1], x[1]))
        return res

    @staticmethod
    def robinson(probs, _):
        """Computes the probability of a message being spam (Robinson's method)
            P = 1 - prod(1-p)^(1/n)
            Q = 1 - prod(p)^(1/n)
            S = (1 + (P-Q)/(P+Q)) / 2
            Courtesy of http://christophe.delord.free.fr/en/index.html
        """

        nth = 1./len(probs)
        P = 1.0 - reduce(operator.mul, map(lambda p: 1.0-p[1], probs), 1.0) ** nth
        Q = 1.0 - reduce(operator.mul, map(lambda p: p[1], probs)) ** nth
        S = (P - Q) / (P + Q)
        return (1 + S) / 2

    @staticmethod
    def robinson_fisher(probs, _):
        """Computes the probability of a message being spam (Robinson-Fisher method)
            H = C-1( -2.ln(prod(p)), 2*n )
            S = C-1( -2.ln(prod(1-p)), 2*n )
            I = (1 + H - S) / 2
            Courtesy of http://christophe.delord.free.fr/en/index.html
        """
        n = len(probs)
        try:
            H = chi_2_p(-2.0 * math.log(reduce(operator.mul, map(lambda p: p[1], probs), 1.0)), 2 * n)
        except OverflowError:
            H = 0.0
        try:
            S = chi_2_p(-2.0 * math.log(reduce(operator.mul, map(lambda p: 1.0 - p[1], probs), 1.0)), 2 * n)
        except OverflowError:
            S = 0.0
        return (1 + H - S) / 2

    def __repr__(self):
        return '<Bayes: %s>' % [self.pools[p] for p in self.pool_names()]

    def __len__(self):
        return len(self.corpus)


class Tokenizer:
    """A simple regex-based whitespace tokenizer.

    It expects a string and can return all tokens lower-cased
    or in their existing case.
    """

    WORD_RE = re.compile('\\w+', re.U)

    def __init__(self, lower=False):
        self.lower = lower

    def tokenize(self, obj):
        for match in self.WORD_RE.finditer(obj):
            if self.lower:
                yield match.group().lower()
            else:
                yield match.group()


def chi_2_p(chi, df):
    """ return P(chisq >= chi, with df degree of freedom)

    df must be even
    """
    assert df & 1 == 0
    m = chi / 2.0
    sum = term = math.exp(-m)
    for i in range(1, df/2):
        term *= m/i
        sum += term
    return min(sum, 1.0)
