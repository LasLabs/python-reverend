
"""
Tests for L{reverend.thomas}.
"""

from unittest import TestCase

from reverend.thomas import Bayes


class TestThomas(TestCase):
    """
    Tests for L{Bayes}.
    """

    def setUp(self):
        super(TestThomas, self).setUp()
        self.bayes = Bayes()

    def test_guess_untrained(self):
        """It should return an empty list when not trained."""
        self.assertEquals(self.bayes.guess("hello, world"), [])

    def test_guess_trained(self):
        """It should return the proper guess when trained."""
        self.bayes.train('fish', 'salmon trout cod carp')
        self.bayes.train('fowl', 'hen chicken duck goose')
        self.assertEquals(
            self.bayes.guess('chicken tikka marsala'),
            [('fowl', 0.9999)],
        )
