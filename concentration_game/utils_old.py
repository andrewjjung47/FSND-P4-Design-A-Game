"""utils.py - File for collecting general utility functions."""

import random
import logging
from google.appengine.ext import ndb
import endpoints

def generate_random_pairs(num_pairs):
    """Creates and returns a list of integer pairs. The pairs are randomly
    positioned in the list."""
    available_pairs = []
    # Generate pairs of integers from 1 to num_pairs
    for count in range(1, num_pairs + 1):
        available_pairs += [count, count]

    random_pairs = []
    # Randomly distribute elements in available_pairs
    for remaining in range(len(available_pairs), 0, -1):
        # Random element from available_pairs will be moved to random_pairs
        random_index = random.randint(0, remaining - 1) 
        random_pairs.append(random_index.pop(random_index))
        
    return random_pairs


def get_by_urlsafe(urlsafe, model):
    """Returns an ndb.Model entity that the urlsafe key points to. Checks
        that the type of entity returned is of the correct kind. Raises an
        error if the key String is malformed or the entity is of the incorrect
        kind
    Args:
        urlsafe: A urlsafe key string
        model: The expected entity kind
    Returns:
        The entity that the urlsafe Key string points to or None if no entity
        exists.
    Raises:
        ValueError:"""
    try:
        key = ndb.Key(urlsafe=urlsafe)
    except TypeError:
        raise endpoints.BadRequestException('Invalid Key')
    except Exception, e:
        if e.__class__.__name__ == 'ProtocolBufferDecodeError':
            raise endpoints.BadRequestException('Invalid Key')
        else:
            raise

    entity = key.get()
    if not entity:
        return None
    if not isinstance(entity, model):
        raise ValueError('Incorrect Kind')
    return entity
