"""models.py - This file contains the class definitions for the Datastore
entities used by the Game. Because these classes are also regular Python
classes they can include methods (such as 'to_form' and 'new_game')."""

import random
from datetime import date
from protorpc import messages
from google.appengine.ext import ndb

from utils import generate_random_pairs

# Make number of pairs as standard 26 pairs for ease of scoring and ranking purposes.
std_num_pairs = 3

class User(ndb.Model):
    """User profile"""
    name = ndb.StringProperty(required=True)
    email =ndb.StringProperty()


class Game(ndb.Model):
    """Game object"""
    pairs = ndb.IntegerProperty(repeated=True)
    guessed_pairs = ndb.IntegerProperty(required=True, default=0)
    attempts_allowed = ndb.IntegerProperty(required=True)
    attempts_remaining = ndb.IntegerProperty(required=True)
    game_over = ndb.BooleanProperty(required=True, default=False)
    user = ndb.KeyProperty(required=True, kind='User')
    history = ndb.StringProperty(repeated=True)

    @classmethod
    def new_game(cls, user, attempts):
        """Creates and returns a new game"""
        # Make the game generate to standard 26 pairs for scoring and ranking purposes
        game = Game(user=user,
                    pairs=generate_random_pairs(std_num_pairs),
                    attempts_allowed=attempts,
                    attempts_remaining=attempts,
                    game_over=False)
        game.put()
        return game

    def card_layout(self):
        # Represent remaining cards as * and guessed cards as G
        layout = []
        for card in self.pairs:
            layout.append('G' if card == -1 else '*')
        # Represent the layout in string
        return '[' + ', '.join(layout) + ']'

    def to_form(self, message=""):
        """Returns a GameForm representation of the Game"""
        form = GameForm()
        form.urlsafe_key = self.key.urlsafe()
        form.user_name = self.user.get().name
        form.attempts_remaining = self.attempts_remaining
        form.game_over = self.game_over
        form.message = message
        form.card_layout = self.card_layout()
        return form

    def make_guess(self, guess1, guess2):
        number1 = self.pairs[guess1] 
        number2 = self.pairs[guess2]

        if number1 == -1 or number2 == -1:
            return self.to_form('These cards are already correctly guessed')
        
        self.attempts_remaining -= 1

        if number1 != number2:
            msg = 'Wrong guess. Number for card {0} is {1} and for card {2} is {3}'.format(guess1,
                number1, guess2, number2)
            result = "Wrong"
        else:
            # Mark correctly guessed pair with -1
            self.guessed_pairs += 1
            self.pairs[guess1] = -1
            self.pairs[guess2] = -1

            msg = 'Correct guess! You have %s pairs remaining.' % (std_num_pairs - self.guessed_pairs)
            result = "Correct"

        if self.guessed_pairs == std_num_pairs:
            self.end_game(True)
            msg = 'You correctly guessed all pairs in %s' % (self.attempts_allowed - self.attempts_remaining)
            result += ", Win"
        elif self.attempts_remaining == 0:
            self.end_game(False)
            msg = 'You ran out of guesses. Game over!'
            result += ", Loss"

        self.history.append('(Guess: [{0}, {1}], Result: {2})'.format(guess1, guess2, result))
        self.put()
        return self.to_form(msg)

    def end_game(self, won=False):
        """Ends the game - if won is True, the player won. - if won is False,
        the player lost."""
        self.game_over = True
        self.put()
        # Add the game to the score 'board'
        score = Score(user=self.user, date=date.today(), won=won,
                      guesses=self.attempts_allowed - self.attempts_remaining,
                      score=float(self.attempts_remaining) / self.attempts_allowed)
        score.put()

        AverageScore.add_score(self.user, score.score)


class Score(ndb.Model):
    """Score object"""
    user = ndb.KeyProperty(required=True, kind='User')
    date = ndb.DateProperty(required=True)
    won = ndb.BooleanProperty(required=True)
    guesses = ndb.IntegerProperty(required=True)
    score = ndb.FloatProperty(required=True)

    def to_form(self):
        return ScoreForm(user_name=self.user.get().name if self.user else None, won=self.won,
                         date=str(self.date), guesses=self.guesses,
                         score=self.score)

class AverageScore(ndb.Model):
    """Average score of a user"""
    user = ndb.KeyProperty(required=True, kind='User')
    num_score = ndb.IntegerProperty(required=True)
    avg_score = ndb.FloatProperty(required=True)

    @classmethod
    def add_score(cls, user, score):
        """Updates average score of a user. Create a new row if nothing exists."""
        avg_score = AverageScore.query(AverageScore.user == user).get()
        if not avg_score:
            return AverageScore(user=user, num_score=1, avg_score=score).put()
        avg_score.num_score += 1
        avg_score.avg_score = (avg_score.avg_score * (avg_score.num_score - 1) + score) / avg_score.num_score
        avg_score.put()

class GameForm(messages.Message):
    """GameForm for outbound game state information"""
    urlsafe_key = messages.StringField(1, required=True)
    attempts_remaining = messages.IntegerField(2, required=True)
    game_over = messages.BooleanField(3, required=True)
    message = messages.StringField(4, required=True)
    user_name = messages.StringField(5, required=True)
    card_layout = messages.StringField(6, required=True)

class GameForms(messages.Message):
    """Return multiple GameForm"""
    items = messages.MessageField(GameForm, 1, repeated=True)

class GameHistoryForm(messages.Message):
    urlsafe_key = messages.StringField(1, required=True)
    history = messages.StringField(2, repeated=True)


class NewGameForm(messages.Message):
    """Used to create a new game"""
    user_name = messages.StringField(1, required=True)
    attempts = messages.IntegerField(2, required=True)


class MakeGuessForm(messages.Message):
    """Used to make a guess in an existing game"""
    guess1 = messages.IntegerField(1, required=True)
    guess2 = messages.IntegerField(2, required=True)


class ScoreForm(messages.Message):
    """ScoreForm for outbound Score information"""
    user_name = messages.StringField(1)
    date = messages.StringField(2, required=True)
    won = messages.BooleanField(3, required=True)
    guesses = messages.IntegerField(4, required=True)
    score = messages.FloatField(5, required=True)


class ScoreForms(messages.Message):
    """Return multiple ScoreForms"""
    items = messages.MessageField(ScoreForm, 1, repeated=True)


class UserRankingForm(messages.Message):
    """Return user rank and score"""
    user_name=messages.StringField(1, required=True)
    rank=messages.IntegerField(2, required=True)
    score=messages.FloatField(3, required=True)



class StringMessage(messages.Message):
    """StringMessage-- outbound (single) string message"""
    message = messages.StringField(1, required=True)
