"""utils.py - File for collecting general utility functions."""

import random

def generate_random_pairs(num_pairs):
    """Creates and returns a list of integer pairs. The pairs are randomly
    positioned in the list."""
    if num_pairs < 2:
        raise ValueError('Number of the pairs should be greater than 1')
    available_pairs = []
    # Generate pairs of integers from 1 to num_pairs
    for count in range(1, num_pairs + 1):
        available_pairs += [count, count]

    random_pairs = []
    # Randomly distribute elements in available_pairs
    for remaining in range(len(available_pairs), 0, -1):
        # Random element from available_pairs will be moved to random_pairs
        random_index = random.randint(0, remaining - 1) 
        random_pairs.append(available_pairs.pop(random_index))
        
    return random_pairs
